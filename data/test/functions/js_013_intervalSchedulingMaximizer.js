export default function intervalSchedulingMaximizer(intervals) {
  if (!intervals.length) return [];
  const sorted = [...intervals].sort((a, b) => a[1] - b[1]);
  const chosen = [sorted[0]];
  let lastEnd = sorted[0][1];
  for (let i = 1; i < sorted.length; i += 1) {
    const [start, end] = sorted[i];
    if (start >= lastEnd) {
      chosen.push(sorted[i]);
      lastEnd = end;
    }
  }
  return chosen;
}
