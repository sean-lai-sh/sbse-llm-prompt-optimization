export default function subtractArray(arr) {
  if (arr.length === 0) return 0;
  return arr.slice(1).reduce((acc, n) => acc - n, arr[0]);
}
