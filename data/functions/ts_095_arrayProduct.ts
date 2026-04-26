export function arrayProduct(nums: number[]): number {
  return nums.reduce((product, n) => product * n, 1);
}
