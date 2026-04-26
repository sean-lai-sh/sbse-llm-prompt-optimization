import time
import functools
from collections import deque
from typing import Any, Callable, Deque, Optional


def rate_limiter(
    calls: int,
    period: float,
    raise_on_limit: bool = False,
    default: Optional[Any] = None
) -> Callable:
    if calls <= 0:
        raise ValueError("calls must be a positive integer")
    if period <= 0:
        raise ValueError("period must be positive")

    def decorator(func: Callable) -> Callable:
        timestamps: Deque[float] = deque()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.monotonic()
            cutoff = now - period
            while timestamps and timestamps[0] < cutoff:
                timestamps.popleft()
            if len(timestamps) >= calls:
                if raise_on_limit:
                    oldest = timestamps[0]
                    wait_time = period - (now - oldest)
                    raise RuntimeError(
                        f"Rate limit exceeded. Try again in {wait_time:.2f}s"
                    )
                return default
            timestamps.append(now)
            return func(*args, **kwargs)

        wrapper.reset = lambda: timestamps.clear()  # type: ignore[attr-defined]
        wrapper.remaining = lambda: max(0, calls - len(timestamps))  # type: ignore[attr-defined]
        return wrapper
    return decorator
