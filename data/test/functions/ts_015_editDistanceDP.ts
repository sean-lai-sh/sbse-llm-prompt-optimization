export function editDistanceDP(
  source: string,
  target: string,
  insertCost = 1,
  deleteCost = 1,
  replaceCost = 1,
): number {
  const m = source.length;
  const n = target.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array<number>(n + 1).fill(0));
  for (let i = 0; i <= m; i += 1) dp[i][0] = i * deleteCost;
  for (let j = 0; j <= n; j += 1) dp[0][j] = j * insertCost;
  for (let i = 1; i <= m; i += 1) {
    for (let j = 1; j <= n; j += 1) {
      if (source[i - 1] === target[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + deleteCost,
          dp[i][j - 1] + insertCost,
          dp[i - 1][j - 1] + replaceCost,
        );
      }
    }
  }
  return dp[m][n];
}
