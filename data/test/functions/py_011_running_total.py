from typing import List


def running_total(nums: List[float]) -> List[float]:
    out: List[float] = []
    total = 0.0
    for n in nums:
        total += n
        out.append(total)
    return out
