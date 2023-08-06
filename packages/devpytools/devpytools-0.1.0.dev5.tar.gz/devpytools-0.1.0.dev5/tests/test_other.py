

from devpytools import replaceFunc


def test_base():

    @replaceFunc(lambda: 5)
    def a() -> int:
        return 4
    assert a() == 5


def test_enabled():

    @replaceFunc(lambda: 5, isEnabled=False)
    def a() -> int:
        return 4
    assert a() == 4


def test_args():

    @replaceFunc(lambda x: 5, isEnabled=True)
    def a(x: int) -> int:
        return x
    assert a(4) == 5

    @replaceFunc(lambda x: 5, isEnabled=False)
    def b(x: int) -> int:
        return x
    assert b(x=4) == 4


def test_filter():

    @replaceFunc(lambda a: a, _filter=lambda x: x['x'] == 5)
    def a(x: int) -> int:
        return 0
    assert a(3) == 0
    assert a(5) == 5
