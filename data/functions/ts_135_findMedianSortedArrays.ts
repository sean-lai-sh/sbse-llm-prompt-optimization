export function findMedianSortedArrays(a: number[], b: number[]): number {
  // Ensure a is the smaller array for binary search
  if (a.length > b.length) return findMedianSortedArrays(b, a);

  const m = a.length;
  const n = b.length;
  let lo = 0;
  let hi = m;

  while (lo <= hi) {
    const partA = Math.floor((lo + hi) / 2);
    const partB = Math.floor((m + n + 1) / 2) - partA;

    const maxLeftA = partA === 0 ? -Infinity : a[partA - 1];
    const minRightA = partA === m ? Infinity : a[partA];
    const maxLeftB = partB === 0 ? -Infinity : b[partB - 1];
    const minRightB = partB === n ? Infinity : b[partB];

    if (maxLeftA <= minRightB && maxLeftB <= minRightA) {
      if ((m + n) % 2 === 0) {
        return (Math.max(maxLeftA, maxLeftB) + Math.min(minRightA, minRightB)) / 2;
      } else {
        return Math.max(maxLeftA, maxLeftB);
      }
    } else if (maxLeftA > minRightB) {
      hi = partA - 1;
    } else {
      lo = partA + 1;
    }
  }

  return 0;
}
