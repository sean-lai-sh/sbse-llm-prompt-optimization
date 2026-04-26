from typing import Dict, List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    seen: Dict[int, int] = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return (seen[complement], i)
        seen[n] = i
    return None
