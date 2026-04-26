export default function normalizeArray(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return [];
  const min = Math.min(...arr);
  const max = Math.max(...arr);
  if (min === max) return arr.map(() => 0);
  const range = max - min;
  return arr.map((n) => (n - min) / range);
}
