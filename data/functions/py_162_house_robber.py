from typing import List


def house_robber(nums: List[int]) -> int:
    if not nums:
        return 0
    prev2, prev1 = 0, 0
    for n in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + n)
    return prev1
