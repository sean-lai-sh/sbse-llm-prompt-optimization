export default function coinChange(coins, amount) {
  if (amount === 0) return { minCoins: 0, combination: [] };

  // dp[i] = minimum number of coins to make amount i
  const dp = new Array(amount + 1).fill(Infinity);
  // coinUsed[i] = the coin denomination used last to reach amount i
  const coinUsed = new Array(amount + 1).fill(-1);
  dp[0] = 0;

  for (let i = 1; i <= amount; i++) {
    for (const coin of coins) {
      if (coin <= i && dp[i - coin] + 1 < dp[i]) {
        dp[i] = dp[i - coin] + 1;
        coinUsed[i] = coin;
      }
    }
  }

  if (dp[amount] === Infinity) {
    return { minCoins: -1, combination: [] };
  }

  // Reconstruct the combination
  const combination = [];
  let remaining = amount;
  while (remaining > 0) {
    combination.push(coinUsed[remaining]);
    remaining -= coinUsed[remaining];
  }

  return { minCoins: dp[amount], combination };
}
