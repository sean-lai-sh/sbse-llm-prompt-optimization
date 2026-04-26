from typing import List


def max_subarray_kadane(nums: List[int]) -> int:
    if not nums:
        return 0
    max_sum = current = nums[0]
    for n in nums[1:]:
        current = max(n, current + n)
        max_sum = max(max_sum, current)
    return max_sum
