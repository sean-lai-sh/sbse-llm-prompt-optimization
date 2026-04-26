export function minArray(nums: number[]): number {
  if (nums.length === 0) throw new RangeError("Array must not be empty");
  return nums.reduce((a, b) => (b < a ? b : a), nums[0]);
}
