export function coinSumWays(amount: number, coins: number[]): number {
  if (amount < 0) return 0;
  const dp = new Array<number>(amount + 1).fill(0);
  dp[0] = 1;
  for (const coin of coins) {
    for (let a = coin; a <= amount; a += 1) {
      dp[a] += dp[a - coin];
    }
  }
  return dp[amount];
}
