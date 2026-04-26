export function parseQueryString(qs: string): Record<string, string> {
  const result: Record<string, string> = {};
  const cleaned = qs.startsWith("?") ? qs.slice(1) : qs;
  if (!cleaned) return result;
  for (const part of cleaned.split("&")) {
    const eqIdx = part.indexOf("=");
    if (eqIdx === -1) {
      result[decodeURIComponent(part)] = "";
    } else {
      const key = decodeURIComponent(part.slice(0, eqIdx));
      const val = decodeURIComponent(part.slice(eqIdx + 1));
      result[key] = val;
    }
  }
  return result;
}
