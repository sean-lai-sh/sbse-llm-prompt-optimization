from collections import deque
from typing import List


def sliding_window_max(nums: List[int], k: int) -> List[int]:
    if not nums or k == 0:
        return []
    dq: deque = deque()
    result = []
    for i, n in enumerate(nums):
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        while dq and nums[dq[-1]] < n:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
