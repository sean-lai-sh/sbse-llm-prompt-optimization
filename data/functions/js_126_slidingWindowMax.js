export default function slidingWindowMax(nums, k) {
  if (!Array.isArray(nums) || nums.length === 0 || k <= 0) return [];
  const result = [];
  const deque = []; // stores indices
  for (let i = 0; i < nums.length; i++) {
    // Remove elements outside window
    while (deque.length > 0 && deque[0] < i - k + 1) deque.shift();
    // Remove smaller elements from back
    while (deque.length > 0 && nums[deque[deque.length - 1]] < nums[i]) deque.pop();
    deque.push(i);
    if (i >= k - 1) result.push(nums[deque[0]]);
  }
  return result;
}
