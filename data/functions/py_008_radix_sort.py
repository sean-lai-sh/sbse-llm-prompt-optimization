from typing import List


def radix_sort(arr: List[int]) -> List[int]:
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        buckets: List[List[int]] = [[] for _ in range(10)]
        for num in arr:
            digit = (num // exp) % 10
            buckets[digit].append(num)
        arr = [num for bucket in buckets for num in bucket]
        exp *= 10
    return arr
