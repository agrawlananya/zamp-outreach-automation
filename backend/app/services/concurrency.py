from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def run_concurrently(fn: Callable[[T], R], items: list[T], max_workers: int = 5) -> list[R]:
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(items))) as executor:
        return list(executor.map(fn, items))
