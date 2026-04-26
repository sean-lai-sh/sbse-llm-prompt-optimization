from typing import Any


def count_occurrences(nested: Any, target: Any) -> int:
    if nested == target:
        return 1
    if isinstance(nested, (list, tuple)):
        return sum(count_occurrences(item, target) for item in nested)
    return 0
