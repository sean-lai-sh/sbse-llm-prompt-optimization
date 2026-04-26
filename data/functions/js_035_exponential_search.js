function binarySearch(arr, target, low, high) {
  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) low = mid + 1;
    else high = mid - 1;
  }
  return -1;
}

export default function exponentialSearch(arr, target) {
  if (arr.length === 0) return -1;
  if (arr[0] === target) return 0;

  let i = 1;
  while (i < arr.length && arr[i] <= target) {
    i *= 2;
  }
  return binarySearch(arr, target, Math.floor(i / 2), Math.min(i, arr.length - 1));
}
