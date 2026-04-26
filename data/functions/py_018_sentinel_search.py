from typing import List, Optional


def sentinel_search(arr: List[int], target: int) -> Optional[int]:
    n = len(arr)
    last = arr[-1] if n > 0 else None
    arr.append(target)
    i = 0
    while arr[i] != target:
        i += 1
    arr.pop()
    if i < n and arr[i] == target:
        return i
    return None
