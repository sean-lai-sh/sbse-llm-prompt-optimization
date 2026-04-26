export default function skylineProblem(buildings) {
  // buildings: [[left, right, height], ...]
  // Returns: array of [x, height] key points defining the skyline

  if (!buildings || buildings.length === 0) return [];

  // Create events: entering a building (+height) and leaving (-height)
  const events = [];
  for (const [left, right, height] of buildings) {
    events.push([left, -height]); // negative = building start
    events.push([right, height]); // positive = building end
  }

  // Sort events: by x, then by height (starts before ends; taller starts first)
  events.sort((a, b) => {
    if (a[0] !== b[0]) return a[0] - b[0];
    return a[1] - b[1];
  });

  // Max-heap simulation using a sorted array of active heights
  // In a production setting, a proper max-heap data structure would be more efficient
  const activeHeights = [0]; // ground level always present
  const result = [];
  let prevMaxHeight = 0;

  for (const [x, h] of events) {
    if (h < 0) {
      // Building starts: add its height to active set
      activeHeights.push(-h);
      activeHeights.sort((a, b) => b - a); // maintain sorted descending
    } else {
      // Building ends: remove its height from active set
      const idx = activeHeights.indexOf(h);
      if (idx !== -1) activeHeights.splice(idx, 1);
    }

    const currentMaxHeight = activeHeights[0];
    if (currentMaxHeight !== prevMaxHeight) {
      result.push([x, currentMaxHeight]);
      prevMaxHeight = currentMaxHeight;
    }
  }

  return result;
}
