from typing import List, Optional


def kth_smallest(arr: List[int], k: int) -> Optional[int]:
    if k < 1 or k > len(arr):
        return None
    pivot = arr[0]
    smaller = [x for x in arr[1:] if x < pivot]
    equal = [x for x in arr if x == pivot]
    larger = [x for x in arr[1:] if x > pivot]
    if k <= len(smaller):
        return kth_smallest(smaller, k)
    if k <= len(smaller) + len(equal):
        return pivot
    return kth_smallest(larger, k - len(smaller) - len(equal))
