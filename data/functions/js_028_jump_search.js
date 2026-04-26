export default function jumpSearch(arr, target) {
  const n = arr.length;
  const step = Math.floor(Math.sqrt(n));
  let prev = 0;
  let curr = step;

  while (curr < n && arr[curr] <= target) {
    prev = curr;
    curr += step;
  }

  for (let i = prev; i < Math.min(curr, n); i++) {
    if (arr[i] === target) return i;
  }
  return -1;
}
