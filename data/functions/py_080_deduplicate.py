from typing import Any, List


def deduplicate(lst: List[Any]) -> List[Any]:
    seen = set()
    result: List[Any] = []
    for item in lst:
        key = item if not isinstance(item, (list, dict)) else str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
