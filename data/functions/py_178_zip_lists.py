from typing import Any, List, Tuple


def zip_lists(l1: List[Any], l2: List[Any]) -> List[Tuple[Any, Any]]:
    length = min(len(l1), len(l2))
    return [(l1[i], l2[i]) for i in range(length)]
