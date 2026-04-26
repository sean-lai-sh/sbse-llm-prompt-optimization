/**
 * Largest Rectangle in Histogram.
 * Given an array of bar heights, find the area of the largest rectangle
 * that fits entirely within the histogram.
 * Uses a monotonic stack for O(n) time.
 */
export function largestRectangleHistogram(heights: number[]): number {
  const n = heights.length;
  const stack: number[] = []; // indices, monotonically increasing heights
  let maxArea = 0;

  for (let i = 0; i <= n; i++) {
    // Use 0 as the sentinel height at the end to flush the stack
    const currentHeight = i === n ? 0 : heights[i];

    while (
      stack.length > 0 &&
      heights[stack[stack.length - 1]] > currentHeight
    ) {
      const h = heights[stack.pop()!];
      // Width: from the new top of stack + 1 to i - 1
      const w = stack.length === 0 ? i : i - stack[stack.length - 1] - 1;
      maxArea = Math.max(maxArea, h * w);
    }

    stack.push(i);
  }

  return maxArea;
}
