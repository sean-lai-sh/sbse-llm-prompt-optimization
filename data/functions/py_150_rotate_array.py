from typing import List


def rotate_array(nums: List[int], k: int) -> List[int]:
    n = len(nums)
    if n == 0:
        return nums
    k = k % n

    def reverse(arr: List[int], lo: int, hi: int) -> None:
        while lo < hi:
            arr[lo], arr[hi] = arr[hi], arr[lo]
            lo += 1
            hi -= 1

    result = nums[:]
    reverse(result, 0, n - 1)
    reverse(result, 0, k - 1)
    reverse(result, k, n - 1)
    return result
