export default function knapsack01(weights, values, capacity) {
  const n = weights.length;
  if (n === 0 || capacity === 0) return { maxValue: 0, items: [] };

  // Build DP table
  const dp = Array.from({ length: n + 1 }, () => new Array(capacity + 1).fill(0));

  for (let i = 1; i <= n; i++) {
    for (let w = 0; w <= capacity; w++) {
      // Don't take item i-1
      dp[i][w] = dp[i - 1][w];
      // Take item i-1 if it fits
      if (weights[i - 1] <= w) {
        const withItem = dp[i - 1][w - weights[i - 1]] + values[i - 1];
        if (withItem > dp[i][w]) {
          dp[i][w] = withItem;
        }
      }
    }
  }

  // Backtrack to find which items were selected
  const items = [];
  let w = capacity;
  for (let i = n; i > 0; i--) {
    if (dp[i][w] !== dp[i - 1][w]) {
      items.unshift(i - 1);
      w -= weights[i - 1];
    }
  }

  return { maxValue: dp[n][capacity], items };
}
