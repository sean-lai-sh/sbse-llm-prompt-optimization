export default function buildQueryString(params) {
  if (typeof params !== "object" || params === null) return "";
  const parts = [];
  for (const [key, value] of Object.entries(params)) {
    const encodedKey = encodeURIComponent(key);
    if (Array.isArray(value)) {
      for (const v of value) parts.push(`${encodedKey}=${encodeURIComponent(v)}`);
    } else if (value === true) {
      parts.push(encodedKey);
    } else if (value !== null && value !== undefined) {
      parts.push(`${encodedKey}=${encodeURIComponent(value)}`);
    }
  }
  return parts.length > 0 ? "?" + parts.join("&") : "";
}
