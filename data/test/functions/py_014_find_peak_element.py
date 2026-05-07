from typing import List


def find_peak_element(nums: List[int]) -> int:
    """Return any index i such that nums[i] > nums[i-1] and nums[i] > nums[i+1].

    Out-of-bounds neighbours are treated as -infinity. Uses binary search in O(log n).
    """
    if not nums:
        raise ValueError("empty input")
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[mid + 1]:
            hi = mid
        else:
            lo = mid + 1
    return lo
