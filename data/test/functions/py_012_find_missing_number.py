from typing import List


def find_missing_number(nums: List[int]) -> int:
    """Given a list containing n distinct numbers in [0, n], return the missing one."""
    n = len(nums)
    expected = n * (n + 1) // 2
    actual = sum(nums)
    return expected - actual
