from typing import List, Optional, Tuple


def coin_change(
    coins: List[int],
    amount: int,
    return_coins: bool = False
) -> Tuple[int, Optional[List[int]]]:
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if not coins:
        raise ValueError("coins list cannot be empty")
    if any(c <= 0 for c in coins):
        raise ValueError("All coin denominations must be positive")

    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    coin_used: List[int] = [-1] * (amount + 1)

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1
                coin_used[i] = coin

    if dp[amount] == float('inf'):
        return (-1, None)

    if not return_coins:
        return (int(dp[amount]), None)

    selected: List[int] = []
    remaining = amount
    while remaining > 0:
        c = coin_used[remaining]
        selected.append(c)
        remaining -= c

    return (int(dp[amount]), selected)
