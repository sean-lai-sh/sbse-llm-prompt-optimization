from typing import List, Tuple


def longest_common_subsequence(
    s1: str,
    s2: str,
    return_sequence: bool = False
) -> Tuple[int, str]:
    if not s1 or not s2:
        return (0, '')

    m, n = len(s1), len(s2)
    dp: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    length = dp[m][n]

    if not return_sequence:
        return (length, '')

    seq_chars: List[str] = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            seq_chars.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return (length, ''.join(reversed(seq_chars)))
