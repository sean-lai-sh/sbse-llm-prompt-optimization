/**
 * Returns the length of the longest strictly increasing subsequence using
 * patience sorting (O(n log n)).
 */
export function longestIncreasingSubsequence(nums: number[]): number {
  if (nums.length === 0) return 0;

  // tails[i] is the smallest tail element of all increasing subsequences
  // of length i+1
  const tails: number[] = [];

  for (const num of nums) {
    let lo = 0;
    let hi = tails.length;

    // Binary search for the leftmost position where tails[mid] >= num
    while (lo < hi) {
      const mid = (lo + hi) >>> 1;
      if (tails[mid] < num) lo = mid + 1;
      else hi = mid;
    }

    tails[lo] = num;
  }

  return tails.length;
}
