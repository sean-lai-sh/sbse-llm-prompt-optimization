import bisect
from typing import List


def longest_increasing_subsequence(nums: List[int]) -> int:
    tails: List[int] = []
    for n in nums:
        pos = bisect.bisect_left(tails, n)
        if pos == len(tails):
            tails.append(n)
        else:
            tails[pos] = n
    return len(tails)
