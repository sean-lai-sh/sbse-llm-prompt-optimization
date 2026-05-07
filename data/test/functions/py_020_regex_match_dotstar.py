def regex_match_dotstar(text: str, pattern: str) -> bool:
    """Check whether ``pattern`` matches the entirety of ``text``.

    The pattern dialect supports literal characters, ``.`` (any single character),
    and ``*`` (zero-or-more of the preceding element). Implemented with a 2D DP
    table in O(len(text) * len(pattern)) time.
    """
    m, n = len(text), len(pattern)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if pattern[j - 1] == "*" and j >= 2:
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            pc = pattern[j - 1]
            if pc == "*":
                dp[i][j] = dp[i][j - 2]
                prev = pattern[j - 2]
                if prev == "." or prev == text[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
            else:
                if pc == "." or pc == text[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
    return dp[m][n]
