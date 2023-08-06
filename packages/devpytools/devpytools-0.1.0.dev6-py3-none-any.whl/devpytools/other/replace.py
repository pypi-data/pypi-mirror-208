from functools import wraps
import inspect
from typing import Any, Callable, Optional, TypeVar, cast
from collections import OrderedDict


FuncType = TypeVar('FuncType', bound=Callable[..., Any])

T = TypeVar('T', bound=Callable[..., Any])


def replaceFunc(replaceFunc: FuncType, *, isEnabled=True,
                _filter: Optional[Callable[["OrderedDict[str, Any]"], bool]] = None):
    '''
    replace wrapped function by replaceFunc
    @param isEnable:
        is replace functionality is enabled
    @param _filter:
        function that determines if original or replace function should be called\n
        if returns True then the replacement one is called
    >>> def devFunc():
    >>>     ...
    >>> @replaceFunc(devFunc, isEnabled=os.getenv("IS_DEV", "")=="true")
    >>> def prodFunc():
    >>>     ...
    '''
    def decorator(func: T) -> T:
        if not isEnabled:
            return func
        signature = inspect.signature(func)

        @wraps(func)
        def decorated(*args, **kwargs):
            if not _filter:
                return replaceFunc(*args, **kwargs)
            if _filter:
                kw = signature.bind(*args, **kwargs)
                if _filter(kw.arguments):
                    return replaceFunc(*args, **kwargs)
            return func(*args, **kwargs)
        return cast(T, decorated)
    return decorator
