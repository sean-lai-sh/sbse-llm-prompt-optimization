export default function productExceptSelf(nums) {
  const n = nums.length;
  const result = new Array(n).fill(1);
  // Left pass: result[i] = product of all nums to the left of i
  let left = 1;
  for (let i = 0; i < n; i++) {
    result[i] = left;
    left *= nums[i];
  }
  // Right pass: multiply by product of all nums to the right of i
  let right = 1;
  for (let i = n - 1; i >= 0; i--) {
    result[i] *= right;
    right *= nums[i];
  }
  return result;
}
