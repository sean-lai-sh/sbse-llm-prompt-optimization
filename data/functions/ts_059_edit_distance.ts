/**
 * Computes the Levenshtein (edit) distance between two strings using
 * bottom-up dynamic programming with O(min(m,n)) space.
 */
export function editDistance(a: string, b: string): number {
  // Ensure b is the shorter string for space optimization
  if (a.length < b.length) [a, b] = [b, a];

  const m = a.length;
  const n = b.length;

  // prev[j] = edit distance between a[0..i-1] and b[0..j-1]
  let prev = Array.from({ length: n + 1 }, (_, j) => j);
  let curr = new Array<number>(n + 1).fill(0);

  for (let i = 1; i <= m; i++) {
    curr[0] = i;
    for (let j = 1; j <= n; j++) {
      if (a[i - 1] === b[j - 1]) {
        curr[j] = prev[j - 1];
      } else {
        curr[j] = 1 + Math.min(
          prev[j],      // deletion
          curr[j - 1],  // insertion
          prev[j - 1]   // substitution
        );
      }
    }
    [prev, curr] = [curr, prev];
  }

  return prev[n];
}
