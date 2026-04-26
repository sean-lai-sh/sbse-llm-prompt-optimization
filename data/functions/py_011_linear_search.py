from typing import List, Optional


def linear_search(arr: List[int], target: int) -> Optional[int]:
    for i, val in enumerate(arr):
        if val == target:
            return i
    return None
