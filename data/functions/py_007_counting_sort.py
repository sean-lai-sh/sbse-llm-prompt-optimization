from typing import List


def counting_sort(arr: List[int]) -> List[int]:
    if not arr:
        return arr
    max_val = max(arr)
    min_val = min(arr)
    range_val = max_val - min_val + 1
    count = [0] * range_val
    for num in arr:
        count[num - min_val] += 1
    result = []
    for i, c in enumerate(count):
        result.extend([i + min_val] * c)
    return result
