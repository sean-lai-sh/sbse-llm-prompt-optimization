import math
from typing import List, Optional


def meta_binary_search(arr: List[int], target: int) -> Optional[int]:
    n = len(arr)
    if n == 0:
        return None
    lg = int(math.log2(n)) + 1
    pos = 0
    for i in range(lg - 1, -1, -1):
        if arr[pos] == target:
            return pos
        new_pos = pos | (1 << i)
        if new_pos < n and arr[new_pos] <= target:
            pos = new_pos
    if arr[pos] == target:
        return pos
    return None
