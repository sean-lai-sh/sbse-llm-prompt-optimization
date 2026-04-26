from typing import Any, Callable, Dict, List


def group_by(items: List[Any], key_func: Callable[[Any], Any]) -> Dict[Any, List[Any]]:
    result: Dict[Any, List[Any]] = {}
    for item in items:
        key = key_func(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result
