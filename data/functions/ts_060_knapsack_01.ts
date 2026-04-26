export interface KnapsackItem {
  weight: number;
  value: number;
}

export interface KnapsackResult {
  maxValue: number;
  selectedItems: number[]; // indices of chosen items
}

/**
 * 0/1 Knapsack solved with bottom-up DP.
 * Returns maximum value and which items were selected.
 */
export function knapsack01(
  items: KnapsackItem[],
  capacity: number
): KnapsackResult {
  const n = items.length;
  // dp[i][w] = max value using items[0..i-1] with capacity w
  const dp: number[][] = Array.from({ length: n + 1 }, () =>
    new Array<number>(capacity + 1).fill(0)
  );

  for (let i = 1; i <= n; i++) {
    const { weight, value } = items[i - 1];
    for (let w = 0; w <= capacity; w++) {
      dp[i][w] = dp[i - 1][w];
      if (weight <= w) {
        dp[i][w] = Math.max(dp[i][w], dp[i - 1][w - weight] + value);
      }
    }
  }

  // Back-track to find selected items
  const selected: number[] = [];
  let w = capacity;
  for (let i = n; i > 0; i--) {
    if (dp[i][w] !== dp[i - 1][w]) {
      selected.push(i - 1);
      w -= items[i - 1].weight;
    }
  }

  return { maxValue: dp[n][capacity], selectedItems: selected.reverse() };
}
