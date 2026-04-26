export default function maxArray(arr) {
  return arr.reduce((max, n) => (n > max ? n : max), arr[0]);
}
