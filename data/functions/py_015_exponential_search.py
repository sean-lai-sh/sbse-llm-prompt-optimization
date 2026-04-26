from typing import List, Optional


def exponential_search(arr: List[int], target: int) -> Optional[int]:
    n = len(arr)
    if n == 0:
        return None
    if arr[0] == target:
        return 0
    i = 1
    while i < n and arr[i] <= target:
        i *= 2
    low, high = i // 2, min(i, n - 1)
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return None
