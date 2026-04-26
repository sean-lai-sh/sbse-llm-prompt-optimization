from typing import List, Tuple


def partition_list(nums: List[int], pivot: int) -> Tuple[List[int], List[int], List[int]]:
    less = [x for x in nums if x < pivot]
    equal = [x for x in nums if x == pivot]
    greater = [x for x in nums if x > pivot]
    return less, equal, greater
