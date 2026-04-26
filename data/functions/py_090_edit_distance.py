from typing import List, Optional, Tuple


def edit_distance(
    s1: str,
    s2: str,
    insert_cost: int = 1,
    delete_cost: int = 1,
    replace_cost: int = 1,
    return_operations: bool = False
) -> Tuple[int, Optional[List[str]]]:
    m, n = len(s1), len(s2)
    dp: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i * delete_cost
    for j in range(n + 1):
        dp[0][j] = j * insert_cost

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + delete_cost,
                    dp[i][j - 1] + insert_cost,
                    dp[i - 1][j - 1] + replace_cost
                )

    distance = dp[m][n]

    if not return_operations:
        return (distance, None)

    ops: List[str] = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            ops.append(f"keep '{s1[i - 1]}'")
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + delete_cost:
            ops.append(f"delete '{s1[i - 1]}'")
            i -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + insert_cost:
            ops.append(f"insert '{s2[j - 1]}'")
            j -= 1
        else:
            ops.append(f"replace '{s1[i - 1]}' -> '{s2[j - 1]}'")
            i -= 1
            j -= 1

    return (distance, list(reversed(ops)))
