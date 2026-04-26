export function mode(nums: number[]): number {
  const freq = new Map<number, number>();
  for (const n of nums) freq.set(n, (freq.get(n) ?? 0) + 1);
  let maxCount = 0;
  let result = nums[0];
  for (const [val, count] of freq) {
    if (count > maxCount) { maxCount = count; result = val; }
  }
  return result;
}
