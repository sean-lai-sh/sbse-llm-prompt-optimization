from typing import Any, Union


def sum_nested(nested: Any) -> Union[int, float]:
    if isinstance(nested, (int, float)):
        return nested
    if isinstance(nested, (list, tuple)):
        return sum(sum_nested(item) for item in nested)
    return 0
