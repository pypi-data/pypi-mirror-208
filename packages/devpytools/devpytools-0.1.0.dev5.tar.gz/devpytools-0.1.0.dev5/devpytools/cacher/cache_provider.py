import abc
from os import PathLike
import os
import pickle
from typing import Any, Callable, Hashable, Dict, Optional, Union
from collections import OrderedDict
from time import time
from pathlib import Path

from .general import _NoValue


class CacheProviderABC(abc.ABC):
    @abc.abstractmethod
    def getData(self, hsh: str, version: str, func: Callable, arguments: "OrderedDict[str, Any]"):
        ...

    @abc.abstractmethod
    def setData(self, hsh: str, version: str, func: Callable, data, arguments: "OrderedDict[str, Any]"):
        ...


class FileCacheProvider(CacheProviderABC):
    def __init__(self, tmpDirPath: Union[str, PathLike] = './tmp',
                 fileNameCreator: Optional[Callable] = None, isExpired: Optional[Callable[[int, Any], bool]] = None,
                 ) -> None:
        self.tmpDirPath = tmpDirPath
        self.fileNameCreator = fileNameCreator or self._getFileName
        self.isExpired = isExpired
        if not Path(self.tmpDirPath).is_dir():
            Path(self.tmpDirPath).mkdir(parents=True, exist_ok=True)

    def _getFileName(self, hsh: str, version: str, func: Callable, arguments):
        return f"{func.__qualname__[:100].replace('<', '').replace('>', '')}V{version}C{hsh}.pkl"

    def getData(self, hsh, version, func, arguments):
        filename = self.fileNameCreator(hsh, version, func, arguments)
        try:
            with open(os.path.join(self.tmpDirPath, filename), 'rb') as f:
                data = pickle.load(f)
                if self.isExpired and self.isExpired(data['timestamp'], data['data']):
                    return _NoValue
                return data['data']
        except FileNotFoundError:
            return _NoValue

    def setData(self, hsh, version, func, data, arguments):
        filename = self.fileNameCreator(hsh, version, func, arguments)
        with open(os.path.join(self.tmpDirPath, filename), 'wb') as f:
            pickle.dump({'data': data, 'timestamp': int(time())}, f)


class InMemoryCacheProvider(CacheProviderABC):
    def __init__(self, isExpired: Optional[Callable[[int, Any], bool]] = None) -> None:
        self._inMemoryCache: Dict[Hashable, Dict[str, Any]] = {}
        self.isExpired = isExpired

    def getData(self, hsh, version, func, arguments):
        data = self._inMemoryCache.get((func.__qualname__, hsh, version), _NoValue)
        if data is _NoValue:
            return data
        if self.isExpired and self.isExpired(data['timestamp'], data['data']):
            return _NoValue
        return data['data']

    def setData(self, hsh, version, func, data, arguments):
        self._inMemoryCache[(func.__qualname__, hsh, version)] = {'data': data, 'timestamp': int(time())}
