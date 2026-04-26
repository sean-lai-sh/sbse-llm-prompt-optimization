export default function pickKeys(obj, keys) {
  if (typeof obj !== "object" || obj === null) return {};
  const pickSet = new Set(Array.isArray(keys) ? keys : [keys]);
  const result = {};
  for (const k of pickSet) {
    if (Object.prototype.hasOwnProperty.call(obj, k)) result[k] = obj[k];
  }
  return result;
}
