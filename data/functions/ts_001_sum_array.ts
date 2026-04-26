export function sumArray(nums: number[]): number {
  return nums.reduce((acc, n) => acc + n, 0);
}
