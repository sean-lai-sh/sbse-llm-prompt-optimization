export function chunkArray<T>(arr: T[], size: number): T[][] {
  if (size <= 0) throw new RangeError("size must be positive");
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}
