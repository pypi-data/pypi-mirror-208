import hashlib
import inspect
import json
from os import PathLike
import re
from typing import Any, Callable, Iterable, List, Optional, Dict, Tuple, TypeVar, Union, cast, overload, Sequence
from functools import wraps
from collections import OrderedDict

from pydashlite import pickPlain

from .general import _NoValue
from .cache_provider import CacheProviderABC, FileCacheProvider, InMemoryCacheProvider


UniqueKeyType = Callable[["OrderedDict[str, Any]"], str]

FuncType = TypeVar('FuncType', bound=Callable[..., Any])

CACHER_MAP: Dict[Optional[str], "Cacher"] = {}

FuncResult = Any


class Cacher:
    def __init__(self, *, name: Optional[str] = None, tmpDirPath: Optional[Union[str, PathLike]] = None,
                 isExpired: Optional[Callable[[int, Any], bool]] = None, isLocal=False,
                 uniqueKey: Optional[Union[UniqueKeyType, Sequence[str]]] = None, isEnable: bool = True,
                 cacheProvider: Optional[CacheProviderABC] = None,
                 isSavable: Optional[Callable[[FuncResult], bool]] = lambda x: bool(x),
                 version=1,
                 **kwargs) -> None:
        '''
        caches results of wrapped time consuming function to accelerate development process
        for other dependent functions
        @param name:
            name what will be used to get this cacher by getCacher, should be unique
        @param tmpDirPath:
            folder where pickled files will be stored, if None inmemory store will be used
        @param isExpired:
            function to determine if cached result is expired
            args is (resultCreationTime, result)
            has pre-prepeared functions in devpytools.cacher.extensions
        @param isLocal:
            if True then the Cacher not added to the global store and cannot be obtained by getCacher func call
        @param uniqueKey:
            list of args to use for unique key creation or
            should return string that represents the result uniqueness by the function args
            used as part of cache filename
            by default picks args of (str, int, float) types and return a hash of their tuple
        @param isEnable:
            is cache functionality is enabled
        @param cacheProvider:
            use given cacheProvider
        @param isSavable:
            function to determine if the result of wrapped function should be cached
            by default only positive results cached
        @param version:
            added to names of cached results and can be used for fast switching
        >>> c = Cacher(tmpDirPath="./tmp")
        >>> c.cache
        >>> def a(b):
        >>>     ...
        # or
        >>> c = Cacher(name="dev", tmpDirPath="./tmp", isEnable=os.getenv("IS_DEV", "")=="true",\
        >>>            isExpired=extensions.expireAfterHours(1), version=1)
        >>> c.cache()
        >>> def a(b):
        >>>     ...
        '''
        if name is None:
            isLocal = True
        if not isLocal:
            if CACHER_MAP.get(name):
                raise ValueError('name should be unique across process')
            CACHER_MAP[name] = self
        self.name = name
        self.tmpDirPath = tmpDirPath
        self.isExpired = isExpired
        self.isLocal = isLocal
        self.isEnable = isEnable
        self.uniqueKey = None
        self.uniqueKeyFields = None
        if uniqueKey:
            if isinstance(uniqueKey, Callable):
                self.uniqueKey = uniqueKey
            elif isinstance(uniqueKey, Iterable):
                self.uniqueKeyFields = uniqueKey
            else:
                raise ValueError("uniqueKey should be function or iterable")
        self.isSavable = isSavable
        self.version = str(version)
        self.cacheProvider = cacheProvider or (FileCacheProvider(tmpDirPath=tmpDirPath, isExpired=isExpired)
                                               if tmpDirPath else InMemoryCacheProvider(isExpired=isExpired))

    def _getUniqueKey(self, arguments) -> str:
        if self.uniqueKeyFields:
            return self._getArgsHash(self._getArgs(pickPlain(arguments, self.uniqueKeyFields)))
        else:
            return self._getArgsHash(self._getArgs(arguments))

    def _getArgs(self, arguments) -> List[Tuple]:
        res = []
        for k, v in arguments.items():
            if k == 'self':
                continue
            res.append((k, v))
        return res

    delMemPat = re.compile(r'object at (\S+)>')

    def __defaultSerializeArgs(self, value):
        try:
            return value.__dict__
        except:  # noqa
            pass
        return self.delMemPat.sub('', str(value))

    def _getArgsHash(self, arguments) -> str:
        return hashlib.sha256((";".join(map(lambda x: json.dumps(x, default=self.__defaultSerializeArgs),
                                            arguments))).encode()).hexdigest()

    @overload
    def cache(self, func: FuncType, *, tmpDirPath: Optional[Union[str, PathLike]] = None,
              isExpired: Optional[Callable[[int, Any], bool]] = None,
              uniqueKey: Optional[Union[UniqueKeyType, Iterable[str]]] = None, isEnable: Optional[bool] = None,
              cacheProvider: Optional[CacheProviderABC] = None,
              isSavable: Optional[Callable[[FuncResult], bool]] = None,
              version=None,) -> FuncType:
        ...

    @overload
    def cache(self, func=None, *, tmpDirPath: Optional[Union[str, PathLike]] = None,
              isExpired: Optional[Callable[[int, Any], bool]] = None,
              uniqueKey: Optional[Union[UniqueKeyType, Iterable[str]]] = None, isEnable: Optional[bool] = None,
              cacheProvider: Optional[CacheProviderABC] = None,
              isSavable: Optional[Callable[[FuncResult], bool]] = None,
              version=None,) -> Callable[[FuncType], FuncType]:
        ...

    def cache(self, func: Optional[FuncType] = None, *, tmpDirPath: Optional[Union[str, PathLike]] = _NoValue,
              isExpired: Optional[Callable[[int, Any], bool]] = _NoValue,
              uniqueKey: Optional[Union[UniqueKeyType, Iterable[str]]] = _NoValue, isEnable: Optional[bool] = _NoValue,
              cacheProvider: Optional[CacheProviderABC] = _NoValue,
              isSavable: Optional[Callable[[FuncResult], bool]] = _NoValue,
              version=_NoValue,):
        '''
        when additional params is passed creates new local Cacher object that merges original Cacher params and the new
        '''
        if not func:
            signature = inspect.signature(self.cache)
            kwargs = {k: v for k, v in locals().items() if k in signature.parameters and v is not _NoValue}
            newself = Cacher(**{**self.__dict__, **kwargs, 'isLocal': True})

            def dec(func):
                return self._getDecorated(func, newself)
            return dec
        return self._getDecorated(func, self)

    @staticmethod
    def _getDecorated(func: FuncType, self: 'Cacher') -> FuncType:
        if not self.isEnable:
            return func
        signature = inspect.signature(func)

        @wraps(func)
        def decorated(*args, **kwargs):
            kw = signature.bind(*args, **kwargs)
            if self.uniqueKey:
                hsh = self.uniqueKey(kw.arguments)
            else:
                hsh = self._getUniqueKey(kw.arguments)
            res = self.cacheProvider.getData(hsh, self.version, func, kw.arguments)
            if res is not _NoValue:
                return res
            res = func(*args, **kwargs)
            if not self.isSavable or self.isSavable(res):
                self.cacheProvider.setData(hsh, self.version, func, res, kw.arguments)
            return res
        return cast(FuncType, decorated)


def getCacher(name: Optional[str] = None):
    '''
    returns previously initiated cacher by name or raise KeyError
    >>> cacher = getCacher()
    # or
    >>> Cacher('dev', tmpDirPath="./tmp")
    ...
    >>> cacher = getCacher('dev')

    >>> @cacher.cache
    >>> def a(b):
    >>>     ...
    # or
    >>> @cacher.cache(tmpDirPath='../tmp2')
    >>> def a(b):
    >>>     ...
    >>> '''
    if name is None and not CACHER_MAP.get(name):
        CACHER_MAP[None] = Cacher(tmpDirPath="./tmp")
    r = CACHER_MAP.get(name)
    if not r:
        raise KeyError(f'cacher {name} not found')
    return r
