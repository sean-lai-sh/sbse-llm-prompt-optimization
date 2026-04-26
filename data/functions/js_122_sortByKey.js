export default function sortByKey(arr, key, direction = "asc") {
  if (!Array.isArray(arr)) return [];
  return arr.slice().sort((a, b) => {
    const av = a[key];
    const bv = b[key];
    if (av === bv) return 0;
    if (av === undefined || av === null) return 1;
    if (bv === undefined || bv === null) return -1;
    const cmp = av < bv ? -1 : 1;
    return direction === "desc" ? -cmp : cmp;
  });
}
