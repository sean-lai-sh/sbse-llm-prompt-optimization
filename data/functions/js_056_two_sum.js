export default function twoSum(nums, target) {
  const seen = new Map();
  const results = [];

  for (let i = 0; i < nums.length; i++) {
    const complement = target - nums[i];

    if (seen.has(complement)) {
      results.push([seen.get(complement), i]);
    }

    // Store the latest index for each value
    seen.set(nums[i], i);
  }

  // Return the first pair found, or null if none
  if (results.length > 0) {
    return results[0];
  }
  return null;
}
