from typing import List, Tuple


def knapsack(
    capacity: int,
    weights: List[int],
    values: List[int],
    return_items: bool = False
) -> Tuple[int, List[int]]:
    if len(weights) != len(values):
        raise ValueError("weights and values must have the same length")
    if capacity < 0:
        raise ValueError("capacity must be non-negative")

    n = len(weights)
    dp: List[List[int]] = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w = weights[i - 1]
        v = values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c:
                with_item = dp[i - 1][c - w] + v
                if with_item > dp[i][c]:
                    dp[i][c] = with_item

    max_value = dp[n][capacity]

    if not return_items:
        return (max_value, [])

    selected: List[int] = []
    remaining = capacity
    for i in range(n, 0, -1):
        if dp[i][remaining] != dp[i - 1][remaining]:
            selected.append(i - 1)
            remaining -= weights[i - 1]

    return (max_value, list(reversed(selected)))
