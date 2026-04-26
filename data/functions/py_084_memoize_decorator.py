import functools
from typing import Any, Callable, Dict, Optional, Tuple


def memoize_decorator(
    max_size: Optional[int] = None,
    typed: bool = False
) -> Callable:
    def decorator(func: Callable) -> Callable:
        cache: Dict[Tuple, Any] = {}
        hits = 0
        misses = 0

        def make_key(args: Tuple, kwargs: Dict) -> Tuple:
            key: list = list(args)
            if kwargs:
                key.append(object())
                for item in sorted(kwargs.items()):
                    key.extend(item)
            if typed:
                key.extend(type(v) for v in args)
                if kwargs:
                    key.extend(type(v) for v in kwargs.values())
            return tuple(key)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses
            key = make_key(args, kwargs)
            if key in cache:
                hits += 1
                return cache[key]
            misses += 1
            result = func(*args, **kwargs)
            if max_size is not None and len(cache) >= max_size:
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            cache[key] = result
            return result

        wrapper.cache = cache  # type: ignore[attr-defined]
        wrapper.cache_info = lambda: {'hits': hits, 'misses': misses, 'size': len(cache)}  # type: ignore[attr-defined]
        wrapper.cache_clear = lambda: cache.clear()  # type: ignore[attr-defined]
        return wrapper
    return decorator
