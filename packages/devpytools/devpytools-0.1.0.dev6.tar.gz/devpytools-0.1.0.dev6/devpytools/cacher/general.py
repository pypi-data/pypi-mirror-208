from typing import cast


class __NoValue:
    def __bool__(self):
        return False


_NoValue = cast(None, __NoValue())


class _UncacheableResult:
    pass
