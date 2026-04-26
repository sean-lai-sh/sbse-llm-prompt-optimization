from typing import List, Tuple


def trapping_rain(
    height: List[int],
    return_per_column: bool = False
) -> Tuple[int, List[int]]:
    if not height:
        return (0, [])

    if any(h < 0 for h in height):
        raise ValueError("Heights must be non-negative")

    n = len(height)

    if n < 3:
        return (0, [0] * n)

    left_max = [0] * n
    right_max = [0] * n
    water = [0] * n

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    total = 0
    for i in range(n):
        trapped = min(left_max[i], right_max[i]) - height[i]
        water[i] = max(0, trapped)
        total += water[i]

    if return_per_column:
        return (total, water)
    return (total, [])
