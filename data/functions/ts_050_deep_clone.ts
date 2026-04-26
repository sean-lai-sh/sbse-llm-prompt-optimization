export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== "object") return obj;
  if (Array.isArray(obj)) {
    return (obj as unknown[]).map((item) => deepClone(item)) as unknown as T;
  }
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
  if (obj instanceof Map) {
    return new Map(
      [...obj.entries()].map(([k, v]) => [deepClone(k), deepClone(v)])
    ) as unknown as T;
  }
  if (obj instanceof Set) {
    return new Set([...obj].map((v) => deepClone(v))) as unknown as T;
  }
  const cloned = Object.create(Object.getPrototypeOf(obj)) as T;
  for (const key of Object.keys(obj as object)) {
    (cloned as Record<string, unknown>)[key] = deepClone(
      (obj as Record<string, unknown>)[key]
    );
  }
  return cloned;
}
