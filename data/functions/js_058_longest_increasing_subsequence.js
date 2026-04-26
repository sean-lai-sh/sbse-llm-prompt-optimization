export default function longestIncreasingSubsequence(nums) {
  if (!nums || nums.length === 0) return [];

  const n = nums.length;
  // dp[i] = length of LIS ending at index i
  const dp = new Array(n).fill(1);
  // parent[i] = index of previous element in LIS ending at i
  const parent = new Array(n).fill(-1);

  let maxLen = 1;
  let maxIdx = 0;

  for (let i = 1; i < n; i++) {
    for (let j = 0; j < i; j++) {
      if (nums[j] < nums[i] && dp[j] + 1 > dp[i]) {
        dp[i] = dp[j] + 1;
        parent[i] = j;
      }
    }
    if (dp[i] > maxLen) {
      maxLen = dp[i];
      maxIdx = i;
    }
  }

  // Reconstruct the subsequence
  const lis = [];
  let idx = maxIdx;
  while (idx !== -1) {
    lis.unshift(nums[idx]);
    idx = parent[idx];
  }

  return lis;
}
