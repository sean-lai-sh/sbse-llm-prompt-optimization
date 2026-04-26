/**
 * Wildcard Pattern Matching.
 * '?' matches any single character, '*' matches any sequence (including empty).
 * Uses bottom-up DP.
 */
export function wildcardMatch(s: string, p: string): boolean {
  const m = s.length;
  const n = p.length;

  // dp[i][j] = does s[0..i-1] match p[0..j-1]?
  const dp: boolean[][] = Array.from({ length: m + 1 }, () =>
    new Array<boolean>(n + 1).fill(false)
  );

  dp[0][0] = true;

  // '*' at the start of pattern can match empty string
  for (let j = 1; j <= n; j++) {
    if (p[j - 1] === "*") dp[0][j] = dp[0][j - 1];
    else break;
  }

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const sc = s[i - 1];
      const pc = p[j - 1];

      if (pc === "*") {
        // '*' matches empty sequence OR one more character
        dp[i][j] = dp[i][j - 1] || dp[i - 1][j];
      } else if (pc === "?" || pc === sc) {
        dp[i][j] = dp[i - 1][j - 1];
      }
    }
  }

  return dp[m][n];
}
