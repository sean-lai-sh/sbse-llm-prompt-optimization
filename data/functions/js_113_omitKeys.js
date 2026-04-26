export default function omitKeys(obj, keys) {
  if (typeof obj !== "object" || obj === null) return {};
  const omitSet = new Set(Array.isArray(keys) ? keys : [keys]);
  const result = {};
  for (const [k, v] of Object.entries(obj)) {
    if (!omitSet.has(k)) result[k] = v;
  }
  return result;
}
