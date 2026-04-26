export default function invertObject(obj) {
  if (typeof obj !== "object" || obj === null) return {};
  const result = {};
  for (const [k, v] of Object.entries(obj)) {
    const strVal = String(v);
    if (strVal in result) {
      result[strVal] = Array.isArray(result[strVal])
        ? [...result[strVal], k]
        : [result[strVal], k];
    } else {
      result[strVal] = k;
    }
  }
  return result;
}
