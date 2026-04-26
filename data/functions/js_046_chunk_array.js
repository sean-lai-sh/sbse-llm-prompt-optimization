export default function chunkArray(arr, size) {
  if (size <= 0) throw new RangeError('Chunk size must be positive');
  const chunks = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}
