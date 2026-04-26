from typing import Any, List


def flatten_nested(nested: Any) -> List[Any]:
    result: List[Any] = []
    if isinstance(nested, (list, tuple)):
        for item in nested:
            result.extend(flatten_nested(item))
    else:
        result.append(nested)
    return result
