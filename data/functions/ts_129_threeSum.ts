export function threeSum(nums: number[]): number[][] {
  const result: number[][] = [];
  const sorted = [...nums].sort((a, b) => a - b);
  const n = sorted.length;

  for (let i = 0; i < n - 2; i++) {
    if (i > 0 && sorted[i] === sorted[i - 1]) continue; // skip duplicates
    let left = i + 1;
    let right = n - 1;

    while (left < right) {
      const sum = sorted[i] + sorted[left] + sorted[right];
      if (sum === 0) {
        result.push([sorted[i], sorted[left], sorted[right]]);
        while (left < right && sorted[left] === sorted[left + 1]) left++;
        while (left < right && sorted[right] === sorted[right - 1]) right--;
        left++;
        right--;
      } else if (sum < 0) {
        left++;
      } else {
        right--;
      }
    }
  }

  return result;
}
