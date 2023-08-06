# devpytools
Tools for development.

## Installation
```
$ pip install devpytools
```

## Usage
### Cacher
Get and use default inmemory cacher
```python
from devpytools import getCacher
c = getCacher()
@c.cache()
def a(b):
    ...
```

Create the cacher that saves a pickled data on disk and can be used between runs
```python
from devpytools import Cacher
c = Cacher(name='dev', tmpDirPath='./tmp')
```

Get previously configured cacher in other file and use
```python
from devpytools import getCacher
c = getCacher("dev")
@c.cache
def a(b):
    ...
```

Example
```python
from devpytools import Cacher
from devpytools.cacher import extensions
IS_DEV = os.getenv("IS_DEV", "") == "true"

devCacher = Cacher(
    name="dev",
    tmpDirPath="./tmp",
    isEnable=IS_DEV,  # work only if run in dev environment
    isExpired=extensions.expireAfterHours(1),  # recache if cached data older than 1 hour
    isSavable=lambda result: bool(result),  # only cache positive function call results
)

@devCacher.cache
def a(b):
    ...

# works with the same params as devCacher but saves caches to ./tmp1 folder
@devCacher.cache(tmpDirPath="./tmp1")
def a1(b):
    ...

# currently disable cache for that func
@devCacher.cache(isEnable=False)
def a2(b):
    ...

# cache only those calls that return more than 0 elements
@devCacher.cache(isSavable=lambda result: result['count'] > 0)
def a3(b):
    ...

# use only a and b arguments to determine unique key of the function call
@devCacher.cache(uniqueKey=lambda args: args['a'] + args['b'])
def a4(a: str, b: str, c: str):
    ...
```
```python
c = getCacher()
# to determine the uniqueness of a function call use only a and b arguments
@c.cache(uniqueKey=("a", "b"))
def a(a, b, c):
    ...
```

### Other
- replaceFunc
```python
from devpytools import replaceFunc
IS_DEV = os.getenv("IS_DEV", "") == "true"

def devFunc():
    # predefined results for development
    ...
# replace only if IS_DEV is True
@replaceFunc(devFunc, isEnabled=IS_DEV)
def prodFunc():
    # time consuming function
    ...
```
