export default function wildcardMatch(s, p) {
  const m = s.length;
  const n = p.length;

  // dp[i][j] = true if s[0..i-1] matches p[0..j-1]
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(false));
  dp[0][0] = true;

  // Handle leading '*' in pattern — '*' can match empty string
  for (let j = 1; j <= n; j++) {
    if (p[j - 1] === '*') {
      dp[0][j] = dp[0][j - 1];
    } else {
      break; // Non-'*' character cannot match empty string
    }
  }

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const pc = p[j - 1];
      const sc = s[i - 1];

      if (pc === '*') {
        // '*' matches empty sequence (dp[i][j-1]) or one+ chars (dp[i-1][j])
        dp[i][j] = dp[i][j - 1] || dp[i - 1][j];
      } else if (pc === '?' || pc === sc) {
        dp[i][j] = dp[i - 1][j - 1];
      }
      // else dp[i][j] remains false
    }
  }

  return dp[m][n];
}
