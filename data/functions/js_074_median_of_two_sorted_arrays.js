export default function medianOfTwoSortedArrays(nums1, nums2) {
  // Ensure nums1 is the smaller array for binary search efficiency
  if (nums1.length > nums2.length) {
    return medianOfTwoSortedArrays(nums2, nums1);
  }

  const m = nums1.length;
  const n = nums2.length;
  const halfLen = Math.floor((m + n + 1) / 2);

  let lo = 0;
  let hi = m;

  while (lo <= hi) {
    const i = Math.floor((lo + hi) / 2); // partition in nums1
    const j = halfLen - i;               // partition in nums2

    if (i < m && nums2[j - 1] > nums1[i]) {
      // i is too small, increase it
      lo = i + 1;
    } else if (i > 0 && nums1[i - 1] > nums2[j]) {
      // i is too big, decrease it
      hi = i - 1;
    } else {
      // i is perfect
      let maxLeft;
      if (i === 0) maxLeft = nums2[j - 1];
      else if (j === 0) maxLeft = nums1[i - 1];
      else maxLeft = Math.max(nums1[i - 1], nums2[j - 1]);

      if ((m + n) % 2 === 1) return maxLeft;

      let minRight;
      if (i === m) minRight = nums2[j];
      else if (j === n) minRight = nums1[i];
      else minRight = Math.min(nums1[i], nums2[j]);

      return (maxLeft + minRight) / 2;
    }
  }

  throw new Error('Input arrays are not sorted');
}
