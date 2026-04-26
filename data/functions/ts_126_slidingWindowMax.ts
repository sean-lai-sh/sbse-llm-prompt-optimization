export function slidingWindowMax(nums: number[], k: number): number[] {
  if (nums.length === 0 || k <= 0) return [];
  const result: number[] = [];
  const deque: number[] = []; // stores indices

  for (let i = 0; i < nums.length; i++) {
    // Remove elements outside the window
    while (deque.length > 0 && deque[0] < i - k + 1) {
      deque.shift();
    }
    // Remove elements smaller than current from back
    while (deque.length > 0 && nums[deque[deque.length - 1]] < nums[i]) {
      deque.pop();
    }
    deque.push(i);
    if (i >= k - 1) {
      result.push(nums[deque[0]]);
    }
  }
  return result;
}
