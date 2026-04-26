from typing import Any, List


def list_unique(lst: List[Any]) -> List[Any]:
    return list(dict.fromkeys(lst))
