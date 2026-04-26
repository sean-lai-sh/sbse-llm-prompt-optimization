export default function arrayAverage(arr) {
  if (arr.length === 0) return 0;
  return arr.reduce((acc, n) => acc + n, 0) / arr.length;
}
