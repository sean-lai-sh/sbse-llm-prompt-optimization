export default function maxSubarrayKadane(nums) {
  if (!nums || nums.length === 0) {
    throw new Error('Array must be non-empty');
  }

  let maxSum = nums[0];
  let currentSum = nums[0];
  let maxStart = 0;
  let maxEnd = 0;
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
      maxStart = tempStart;
      maxEnd = i;
    }
  }

  return {
    maxSum,
    subarray: nums.slice(maxStart, maxEnd + 1),
    startIndex: maxStart,
    endIndex: maxEnd,
  };
}
