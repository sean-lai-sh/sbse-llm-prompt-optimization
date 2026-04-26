export function jumpSearch(arr: number[], target: number): number {
  const n = arr.length;
  if (n === 0) return -1;
  const step = Math.floor(Math.sqrt(n));
  let prev = 0, curr = step;

  while (curr < n && arr[curr] <= target) {
    prev = curr;
    curr += step;
  }

  for (let i = prev; i < Math.min(curr, n); i++) {
    if (arr[i] === target) return i;
  }
  return -1;
}
