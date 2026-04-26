from collections import OrderedDict
from typing import Any, Callable, Hashable, Optional, Tuple


def lru_cache_impl(capacity: int = 128) -> Callable:
    if capacity < 1:
        raise ValueError("capacity must be at least 1")

    def decorator(func: Callable) -> Callable:
        cache: OrderedDict = OrderedDict()
        hits = 0
        misses = 0

        def make_key(args: Tuple, kwargs: dict) -> Hashable:
            try:
                return (args, tuple(sorted(kwargs.items())))
            except TypeError:
                return (str(args), str(sorted(kwargs.items())))

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses
            key = make_key(args, kwargs)
            if key in cache:
                hits += 1
                cache.move_to_end(key)
                return cache[key]
            misses += 1
            result = func(*args, **kwargs)
            cache[key] = result
            cache.move_to_end(key)
            if len(cache) > capacity:
                cache.popitem(last=False)
            return result

        wrapper.__wrapped__ = func  # type: ignore[attr-defined]
        wrapper.cache_info = lambda: {  # type: ignore[attr-defined]
            'hits': hits, 'misses': misses,
            'capacity': capacity, 'current_size': len(cache)
        }
        wrapper.cache_clear = lambda: (cache.clear(), None)[1]  # type: ignore[attr-defined]
        wrapper.cache_peek = lambda *a, **kw: cache.get(make_key(a, kw))  # type: ignore[attr-defined]
        return wrapper

    return decorator
