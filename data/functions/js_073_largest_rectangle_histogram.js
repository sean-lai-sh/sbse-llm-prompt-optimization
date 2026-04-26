export default function largestRectangleHistogram(heights) {
  if (!heights || heights.length === 0) return 0;

  const n = heights.length;
  const stack = []; // stack of indices
  let maxArea = 0;

  for (let i = 0; i <= n; i++) {
    const currentHeight = i === n ? 0 : heights[i];

    // Pop bars that are taller than current bar
    while (stack.length > 0 && currentHeight < heights[stack[stack.length - 1]]) {
      const height = heights[stack.pop()];
      // Width extends to current i on the right, and stack top + 1 on the left
      const width = stack.length === 0 ? i : i - stack[stack.length - 1] - 1;
      const area = height * width;
      if (area > maxArea) {
        maxArea = area;
      }
    }

    stack.push(i);
  }

  return maxArea;
}
