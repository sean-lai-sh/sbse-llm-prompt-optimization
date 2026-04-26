export default function flattenObject(obj, prefix = "", separator = ".") {
  if (typeof obj !== "object" || obj === null) return {};
  const result = {};
  for (const [key, value] of Object.entries(obj)) {
    const newKey = prefix ? `${prefix}${separator}${key}` : key;
    if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      Object.assign(result, flattenObject(value, newKey, separator));
    } else {
      result[newKey] = value;
    }
  }
  return result;
}
