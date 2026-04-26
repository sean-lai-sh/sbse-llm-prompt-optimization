/**
 * Finds the median of two sorted arrays in O(log(min(m, n))) time.
 * Uses binary search on the shorter array.
 */
export function medianOfTwoSortedArrays(
  nums1: number[],
  nums2: number[]
): number {
  // Ensure nums1 is the shorter array
  if (nums1.length > nums2.length) return medianOfTwoSortedArrays(nums2, nums1);

  const m = nums1.length;
  const n = nums2.length;
  const halfLen = Math.floor((m + n + 1) / 2);

  let lo = 0;
  let hi = m;

  while (lo <= hi) {
    const i = (lo + hi) >>> 1; // partition index in nums1
    const j = halfLen - i;      // partition index in nums2

    const maxLeft1  = i === 0 ? -Infinity : nums1[i - 1];
    const minRight1 = i === m ?  Infinity : nums1[i];
    const maxLeft2  = j === 0 ? -Infinity : nums2[j - 1];
    const minRight2 = j === n ?  Infinity : nums2[j];

    if (maxLeft1 <= minRight2 && maxLeft2 <= minRight1) {
      // Correct partition found
      const maxLeft  = Math.max(maxLeft1, maxLeft2);
      const minRight = Math.min(minRight1, minRight2);

      if ((m + n) % 2 === 1) return maxLeft;
      return (maxLeft + minRight) / 2;
    } else if (maxLeft1 > minRight2) {
      hi = i - 1;
    } else {
      lo = i + 1;
    }
  }

  throw new Error("Input arrays are not sorted");
}
