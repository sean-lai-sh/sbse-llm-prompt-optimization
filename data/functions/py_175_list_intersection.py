from typing import Any, List


def list_intersection(l1: List[Any], l2: List[Any]) -> List[Any]:
    s = set(l2)
    seen = set()
    result = []
    for item in l1:
        if item in s and item not in seen:
            result.append(item)
            seen.add(item)
    return result
