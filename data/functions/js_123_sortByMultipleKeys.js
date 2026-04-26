export default function sortByMultipleKeys(arr, criteria) {
  // criteria: [{ key, direction }]
  if (!Array.isArray(arr)) return [];
  if (!Array.isArray(criteria) || criteria.length === 0) return arr.slice();
  return arr.slice().sort((a, b) => {
    for (const { key, direction = "asc" } of criteria) {
      const av = a[key];
      const bv = b[key];
      if (av === bv) continue;
      if (av === undefined || av === null) return 1;
      if (bv === undefined || bv === null) return -1;
      const cmp = av < bv ? -1 : 1;
      return direction === "desc" ? -cmp : cmp;
    }
    return 0;
  });
}
