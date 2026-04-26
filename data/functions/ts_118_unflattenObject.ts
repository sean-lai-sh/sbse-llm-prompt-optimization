export function unflattenObject(flat: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [path, value] of Object.entries(flat)) {
    const keys = path.split(".");
    let current: Record<string, unknown> = result;
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (typeof current[k] !== "object" || current[k] === null) {
        current[k] = {};
      }
      current = current[k] as Record<string, unknown>;
    }
    current[keys[keys.length - 1]] = value;
  }
  return result;
}
