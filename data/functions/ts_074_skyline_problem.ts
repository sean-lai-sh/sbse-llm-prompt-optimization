export interface Building {
  left: number;
  right: number;
  height: number;
}

export type SkylinePoint = [number, number]; // [x, height]

/**
 * Skyline Problem.
 * Given a list of buildings, compute the skyline outline as a list of
 * critical points (x, height) where the height changes.
 *
 * Uses a divide-and-conquer merge approach (O(n log n)).
 */
export function skylineProblem(buildings: Building[]): SkylinePoint[] {
  if (buildings.length === 0) return [];

  function mergeSkylines(
    left: SkylinePoint[],
    right: SkylinePoint[]
  ): SkylinePoint[] {
    const result: SkylinePoint[] = [];
    let i = 0, j = 0;
    let h1 = 0, h2 = 0;

    while (i < left.length && j < right.length) {
      let x: number;
      if (left[i][0] < right[j][0]) {
        x = left[i][0];
        h1 = left[i][1];
        i++;
      } else if (right[j][0] < left[i][0]) {
        x = right[j][0];
        h2 = right[j][1];
        j++;
      } else {
        x = left[i][0];
        h1 = left[i][1];
        h2 = right[j][1];
        i++; j++;
      }
      const maxH = Math.max(h1, h2);
      if (result.length === 0 || result[result.length - 1][1] !== maxH) {
        result.push([x, maxH]);
      }
    }

    while (i < left.length) result.push(left[i++]);
    while (j < right.length) result.push(right[j++]);

    return result;
  }

  function solve(lo: number, hi: number): SkylinePoint[] {
    if (lo === hi) {
      const { left, right, height } = buildings[lo];
      return [[left, height], [right, 0]];
    }
    const mid = (lo + hi) >>> 1;
    return mergeSkylines(solve(lo, mid), solve(mid + 1, hi));
  }

  return solve(0, buildings.length - 1);
}
