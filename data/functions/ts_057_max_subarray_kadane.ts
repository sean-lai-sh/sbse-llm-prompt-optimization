export interface SubarrayResult {
  maxSum: number;
  startIndex: number;
  endIndex: number;
}

/**
 * Kadane's algorithm to find the contiguous subarray with the largest sum.
 * Returns the max sum and the inclusive indices of that subarray.
 */
export function maxSubarrayKadane(nums: number[]): SubarrayResult {
  if (nums.length === 0) throw new RangeError("Array must not be empty");

  let maxSum = nums[0];
  let currentSum = nums[0];
  let start = 0;
  let end = 0;
  let tempStart = 0;

  for (let i = 1; i < nums.length; i++) {
    if (currentSum + nums[i] < nums[i]) {
      currentSum = nums[i];
      tempStart = i;
    } else {
      currentSum += nums[i];
    }

    if (currentSum > maxSum) {
      maxSum = currentSum;
      start = tempStart;
      end = i;
    }
  }

  return { maxSum, startIndex: start, endIndex: end };
}
