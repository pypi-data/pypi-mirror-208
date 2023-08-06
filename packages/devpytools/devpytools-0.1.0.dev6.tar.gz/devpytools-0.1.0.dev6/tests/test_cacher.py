import pytest
from time import time
import os
import shutil

from devpytools import Cacher, getCacher, FileCacheProvider, CacheProviderABC
from devpytools.cacher.cacher import CACHER_MAP

TMP_DIR_PATH = f'./tmp{int(time())}'


@pytest.fixture()
def inmemResourceSetup(request):
    os.mkdir(TMP_DIR_PATH)

    def resource_teardown():
        c = getCacher(None)
        CACHER_MAP.clear()
        CACHER_MAP[None] = c
        shutil.rmtree(TMP_DIR_PATH)
    request.addfinalizer(resource_teardown)


@pytest.fixture()
def fileResourceSetup(request):
    os.mkdir(TMP_DIR_PATH)

    def resource_teardown():
        c = CACHER_MAP[None]
        CACHER_MAP.clear()
        CACHER_MAP[None] = c
        shutil.rmtree(TMP_DIR_PATH)
    request.addfinalizer(resource_teardown)


def countFiles(path=TMP_DIR_PATH):
    return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])



def test_base(inmemResourceSetup):
    c = Cacher(name='test')
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 4
    assert a(2) == 4
    var = 7
    assert a(1) == 4
    assert a(3) == 7


def test_fileBase(fileResourceSetup):
    c = Cacher(name='test', tmpDirPath=TMP_DIR_PATH)
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 4
    assert a(2) == 4
    var = 7
    assert a(1) == 4
    assert a(3) == 7
    assert countFiles() != 0


def test_folderCreation(fileResourceSetup):
    path = TMP_DIR_PATH + "/tmp2"
    c = Cacher(name='test', tmpDirPath=path)
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 4
    var = 7
    assert a(1) == 4
    assert countFiles(path) != 0


def test_getCacher(inmemResourceSetup):
    c = getCacher()
    try:
        getCacher('test')
    except KeyError:
        pass
    else:
        raise Exception('KeyError is not raised')
    Cacher(name='test')
    c2 = getCacher('test')
    var = 4

    @c.cache
    def a(a):
        return var

    @c2.cache
    def a2(a):
        return var
    assert a(1) == 4
    var = 5
    assert a2(1) == 5
    var = 7
    assert a(1) == 4
    assert a2(1) == 5


def test_globalCachers(inmemResourceSetup):
    c = Cacher(name='test')
    with pytest.raises(ValueError):
        c = Cacher(name='test')


def test_uniqKey(inmemResourceSetup):
    c = Cacher(name='test')
    var = 4

    @c.cache
    def a(a):
        return var

    @c.cache(uniqueKey=lambda *a, **b: 'True')
    def a1(a):
        return var
    assert a(1) == 4
    assert a1(1) == 4
    var = 7
    assert a(2) == 7
    assert a1(2) == 4


def test_uniqKeyArgs(inmemResourceSetup):
    c = Cacher(name='test')
    var = 4

    @c.cache(uniqueKey=lambda args: args["a"]+args['b'])
    def a1(a, b):
        return var
    assert a1(1, b=2.5) == 4
    var = 7
    assert a1(2.5, b=1) == 4


def test_uniqKeyFields(inmemResourceSetup):
    c = Cacher(name='test', tmpDirPath=TMP_DIR_PATH)
    var = 4

    @c.cache(uniqueKey=('a', 'b'))
    def a1(a, b, c):
        return var
    assert a1(1, b=2, c=3) == 4
    var = 7
    assert a1(b=2, a=1, c=1) == 4


def test_expired(inmemResourceSetup):
    c = Cacher(name='test', isExpired=lambda x, y: True)
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 4
    var = 7
    assert a(1) == 7


def test_expiredArgs(inmemResourceSetup):
    c = Cacher(name='test', isExpired=lambda x, y: time() > x and y == 4)
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 4
    var = 7
    assert a(1) == 7
    var = 4
    assert a(1) == 7


def test_enabled(inmemResourceSetup):
    c = Cacher(name='test', isEnable=False)
    var = 4

    @c.cache
    def a(a):
        return var
    assert a("1") == 4
    var = 7
    assert a("1") == 7


def test_cacheProvider(inmemResourceSetup):
    class Ctest(CacheProviderABC):
        def getData(self, hsh, func, *args, **kwargs):
            return 5

        def setData(self, hsh, func, data, *args, **kwargs):
            return 5

    c = Cacher(name='test', cacheProvider=Ctest())
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 5


def test_expireExtensionsInmemory(inmemResourceSetup, monkeypatch):
    import time
    tm = time.time()

    def monkeyTime():
        return tm
    from devpytools.cacher import extensions
    monkeypatch.setattr(extensions, "time", monkeyTime)
    c = Cacher(name='test', isExpired=extensions.expireAfterMinutes(1))
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 4
    var = 7
    assert a(1) == 4
    tm += 61
    assert a(1) == 7

    c = Cacher(name='test1', isExpired=extensions.expireAfterHours(1))
    var = 4

    @c.cache
    def b(a):
        return var
    assert b(1) == 4
    var = 7
    assert b(1) == 4
    tm += 3600
    assert b(1) == 7

    c = Cacher(name='test2', isExpired=extensions.expireAfterDays(1))
    var = 4

    @c.cache
    def d(a):
        return var
    assert d(1) == 4
    var = 7
    assert d(1) == 4
    tm += 24*3600
    assert d(1) == 7


def test_expireExtensionsFile(inmemResourceSetup, monkeypatch):
    import time
    tm = time.time()

    def monkeyTime():
        return tm
    from devpytools.cacher import extensions
    monkeypatch.setattr(extensions, "time", monkeyTime)
    c = Cacher(name='test', isExpired=extensions.expireAfterMinutes(1), tmpDirPath=TMP_DIR_PATH)
    var = 4

    @c.cache
    def a(a):
        return var
    assert a(1) == 4
    var = 7
    assert a(1) == 4
    tm += 61
    assert a(1) == 7


def test_version(inmemResourceSetup):
    c1 = Cacher(name='test1', tmpDirPath=TMP_DIR_PATH, version=1)
    c2 = Cacher(name='test2', tmpDirPath=TMP_DIR_PATH, version=2)
    c3 = Cacher(name='test3', tmpDirPath=TMP_DIR_PATH, version=1)
    var = 4

    @c1.cache
    def a(a):  # type: ignore
        return var
    a1 = a

    @c2.cache
    def a(a):  # type: ignore
        return var
    a2 = a

    @c3.cache
    def a(a):
        return var
    a3 = a
    assert a1(1) == 4
    var = 7
    assert a2(1) == 7

    assert a1(1) == 4
    assert a1(1) == a3(1)
    var = 4
    assert a2(1) == 7


def test_isSavable(inmemResourceSetup):
    c = Cacher(name='test', isSavable=lambda x: x == 4)
    var = 4

    @c.cache
    def a(a):
        return var
    assert a("1") == 4
    var = 7
    assert a("1") == 4
    assert a(2.6) == 7
    var = 4
    assert a(2.6) == 4


def test_wrapClass(inmemResourceSetup):
    c = Cacher(name='test')
    var = 4

    class A:
        @c.cache
        def a(self, a):
            return var
    a = A()
    assert a.a("a") == 4
    var = 7
    assert a.a("a") == 4


def test_variousArgs(inmemResourceSetup):
    c = Cacher(name='test', tmpDirPath=TMP_DIR_PATH)
    var = 4

    class A:
        pass

    @c.cache
    def a(a, b, c, d, e):
        return var
    assert a("a", (1, 2), ([1],), {}, A()) == 4
    var = 7
    assert a("a", (1, 2), ([1],), {}, A()) == 4


def test_updatedCache(inmemResourceSetup):
    c = Cacher(name='test', uniqueKey=('a', 'b'), version=2, tmpDirPath=TMP_DIR_PATH)
    var = 4

    @c.cache(uniqueKey=('a', 'b'))
    def a1(a, b, c):
        return var
    assert a1(1, b=2, c=3) == 4
    var = 7
    assert a1(b=2, a=1, c=1) == 4
