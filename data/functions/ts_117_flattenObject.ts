export function flattenObject(
  obj: Record<string, unknown>,
  prefix: string = ""
): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (value !== null && typeof value === "object" && !Array.isArray(value)) {
      const nested = flattenObject(value as Record<string, unknown>, fullKey);
      Object.assign(result, nested);
    } else {
      result[fullKey] = value;
    }
  }
  return result;
}
