export function invertObject<K extends string, V extends string>(
  obj: Record<K, V>
): Record<V, K> {
  const result = {} as Record<V, K>;
  for (const [key, value] of Object.entries(obj) as [K, V][]) {
    result[value] = key;
  }
  return result;
}
