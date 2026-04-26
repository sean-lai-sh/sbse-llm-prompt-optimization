export function normalizeArray(nums: number[]): number[] {
  if (nums.length === 0) return [];
  const min = Math.min(...nums);
  const max = Math.max(...nums);
  const range = max - min;
  if (range === 0) return nums.map(() => 0);
  return nums.map((n) => (n - min) / range);
}
