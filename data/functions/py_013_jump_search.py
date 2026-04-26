import math
from typing import List, Optional


def jump_search(arr: List[int], target: int) -> Optional[int]:
    n = len(arr)
    step = int(math.sqrt(n))
    prev = 0
    while prev < n and arr[min(step, n) - 1] < target:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return None
    for i in range(prev, min(step, n)):
        if arr[i] == target:
            return i
    return None
