export default function parseQueryString(qs) {
  if (typeof qs !== "string") return {};
  const query = qs.startsWith("?") ? qs.slice(1) : qs;
  if (query.length === 0) return {};
  const result = {};
  for (const pair of query.split("&")) {
    const eqIdx = pair.indexOf("=");
    if (eqIdx === -1) {
      const key = decodeURIComponent(pair);
      if (key) result[key] = true;
    } else {
      const key = decodeURIComponent(pair.slice(0, eqIdx));
      const value = decodeURIComponent(pair.slice(eqIdx + 1));
      if (key in result) {
        result[key] = Array.isArray(result[key]) ? [...result[key], value] : [result[key], value];
      } else {
        result[key] = value;
      }
    }
  }
  return result;
}
