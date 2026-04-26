export default function nextPermutation(nums) {
  const arr = nums.slice();
  const n = arr.length;
  // Find largest index i such that arr[i] < arr[i+1]
  let i = n - 2;
  while (i >= 0 && arr[i] >= arr[i + 1]) i--;
  if (i >= 0) {
    // Find largest index j such that arr[j] > arr[i]
    let j = n - 1;
    while (arr[j] <= arr[i]) j--;
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  // Reverse from i+1 to end
  let left = i + 1, right = n - 1;
  while (left < right) {
    [arr[left], arr[right]] = [arr[right], arr[left]];
    left++;
    right--;
  }
  return arr;
}
