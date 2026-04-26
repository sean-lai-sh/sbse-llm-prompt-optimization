export default function mergeIntervals(intervals) {
  if (!intervals || intervals.length === 0) return [];

  // Sort by start time
  const sorted = [...intervals].sort((a, b) => a[0] - b[0]);
  const merged = [sorted[0]];

  for (let i = 1; i < sorted.length; i++) {
    const current = sorted[i];
    const last = merged[merged.length - 1];

    if (current[0] <= last[1]) {
      // Overlapping: extend the end if needed
      last[1] = Math.max(last[1], current[1]);
    } else {
      // Non-overlapping: add as a new interval
      merged.push([...current]);
    }
  }

  return merged;
}
