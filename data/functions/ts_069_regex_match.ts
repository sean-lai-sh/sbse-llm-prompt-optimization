/**
 * Regular Expression Matching.
 * Supports '.' (any single character) and '*' (zero or more of preceding).
 * Uses bottom-up DP.
 */
export function regularExpressionMatch(s: string, p: string): boolean {
  const m = s.length;
  const n = p.length;

  // dp[i][j] = does s[0..i-1] match p[0..j-1]?
  const dp: boolean[][] = Array.from({ length: m + 1 }, () =>
    new Array<boolean>(n + 1).fill(false)
  );

  dp[0][0] = true;

  // Handle patterns like a*, a*b*, a*b*c* that can match empty string
  for (let j = 2; j <= n; j++) {
    if (p[j - 1] === "*") {
      dp[0][j] = dp[0][j - 2];
    }
  }

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const sc = s[i - 1];
      const pc = p[j - 1];

      if (pc === "*") {
        // Option 1: use '*' as zero occurrences of preceding character
        dp[i][j] = dp[i][j - 2];
        // Option 2: use '*' as one or more, if preceding char matches
        if (!dp[i][j] && j >= 2) {
          const prev = p[j - 2];
          if (prev === "." || prev === sc) {
            dp[i][j] = dp[i - 1][j];
          }
        }
      } else if (pc === "." || pc === sc) {
        dp[i][j] = dp[i - 1][j - 1];
      }
    }
  }

  return dp[m][n];
}
