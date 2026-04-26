export interface Interval {
  start: number;
  end: number;
}

/**
 * Given an array of intervals, merge all overlapping intervals and return
 * the resulting array of non-overlapping intervals sorted by start.
 */
export function mergeIntervals(intervals: Interval[]): Interval[] {
  if (intervals.length === 0) return [];

  // Sort by start time
  const sorted = [...intervals].sort((a, b) => a.start - b.start);

  const merged: Interval[] = [{ ...sorted[0] }];

  for (let i = 1; i < sorted.length; i++) {
    const current = sorted[i];
    const last = merged[merged.length - 1];

    if (current.start <= last.end) {
      // Overlapping: extend the last interval if needed
      last.end = Math.max(last.end, current.end);
    } else {
      // Non-overlapping: start a new interval
      merged.push({ ...current });
    }
  }

  return merged;
}
