export function nextPermutation(nums: number[]): number[] {
  const arr = [...nums];
  const n = arr.length;

  // Find the largest index i such that arr[i] < arr[i + 1]
  let i = n - 2;
  while (i >= 0 && arr[i] >= arr[i + 1]) i--;

  if (i >= 0) {
    // Find the largest index j such that arr[i] < arr[j]
    let j = n - 1;
    while (arr[j] <= arr[i]) j--;
    // Swap arr[i] and arr[j]
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }

  // Reverse the suffix starting at arr[i + 1]
  let left = i + 1;
  let right = n - 1;
  while (left < right) {
    [arr[left], arr[right]] = [arr[right], arr[left]];
    left++;
    right--;
  }

  return arr;
}
