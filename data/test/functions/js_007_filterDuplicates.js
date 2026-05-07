export default function filterDuplicates(arr) {
  const counts = new Map();
  for (const item of arr) {
    counts.set(item, (counts.get(item) || 0) + 1);
  }
  return arr.filter((item) => counts.get(item) === 1);
}
