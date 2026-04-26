from typing import List


def merge_sorted_lists(l1: List[int], l2: List[int]) -> List[int]:
    result = []
    i = j = 0
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]:
            result.append(l1[i])
            i += 1
        else:
            result.append(l2[j])
            j += 1
    result.extend(l1[i:])
    result.extend(l2[j:])
    return result
