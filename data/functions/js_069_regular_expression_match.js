export default function regularExpressionMatch(s, p) {
  const m = s.length;
  const n = p.length;

  // dp[i][j] = true if s[0..i-1] matches p[0..j-1]
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(false));
  dp[0][0] = true;

  // Handle patterns like a*, a*b*, a*b*c* that can match empty string
  for (let j = 2; j <= n; j++) {
    if (p[j - 1] === '*') {
      dp[0][j] = dp[0][j - 2];
    }
  }

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const pc = p[j - 1];
      const sc = s[i - 1];

      if (pc === '*') {
        // Zero occurrences of preceding element
        dp[i][j] = dp[i][j - 2];
        // One or more occurrences if the preceding element matches
        if (!dp[i][j] && j >= 2) {
          const prev = p[j - 2];
          if (prev === '.' || prev === sc) {
            dp[i][j] = dp[i - 1][j];
          }
        }
      } else if (pc === '.' || pc === sc) {
        dp[i][j] = dp[i - 1][j - 1];
      }
    }
  }

  return dp[m][n];
}
