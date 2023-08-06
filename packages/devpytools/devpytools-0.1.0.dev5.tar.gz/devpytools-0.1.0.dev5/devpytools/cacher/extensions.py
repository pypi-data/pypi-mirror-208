from datetime import timedelta
from time import time
from typing import Callable, Any


__all__ = [
    'expireAfterDays',
    'expireAfterHours',
    'expireAfterMinutes',
]


def expireAfterDays(days=1) -> Callable[[int, Any], bool]:
    t = timedelta(days=days).total_seconds()
    return lambda *x: x[0] < time() - t


def expireAfterHours(hours=1) -> Callable[[int, Any], bool]:
    t = timedelta(hours=hours).total_seconds()
    return lambda *x: x[0] < time() - t


def expireAfterMinutes(minutes=1) -> Callable[[int, Any], bool]:
    t = timedelta(minutes=minutes).total_seconds()
    return lambda *x: x[0] < time() - t
