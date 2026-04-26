export interface CoinChangeResult {
  minCoins: number;      // -1 if impossible
  coins: number[];       // actual coins used
}

/**
 * Classic coin-change problem: find the minimum number of coins that sum to
 * `amount`, reconstructing which coins were used.
 */
export function coinChange(
  denominations: number[],
  amount: number
): CoinChangeResult {
  if (amount < 0) return { minCoins: -1, coins: [] };
  if (amount === 0) return { minCoins: 0, coins: [] };

  const INF = amount + 1;
  // dp[i] = min coins to make amount i
  const dp = new Array<number>(amount + 1).fill(INF);
  // parent[i] = coin used to reach amount i
  const parent = new Array<number>(amount + 1).fill(-1);
  dp[0] = 0;

  for (let i = 1; i <= amount; i++) {
    for (const coin of denominations) {
      if (coin <= i && dp[i - coin] + 1 < dp[i]) {
        dp[i] = dp[i - coin] + 1;
        parent[i] = coin;
      }
    }
  }

  if (dp[amount] === INF) return { minCoins: -1, coins: [] };

  // Reconstruct coin sequence
  const coins: number[] = [];
  let remaining = amount;
  while (remaining > 0) {
    const coin = parent[remaining];
    coins.push(coin);
    remaining -= coin;
  }

  return { minCoins: dp[amount], coins };
}
