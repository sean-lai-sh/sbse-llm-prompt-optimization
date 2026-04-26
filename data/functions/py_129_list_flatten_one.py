from typing import Any, List


def list_flatten_one(lst: List[List[Any]]) -> List[Any]:
    return [item for sublist in lst for item in sublist]
