export default function zipArrays(...arrays) {
  const minLen = Math.min(...arrays.map(a => a.length));
  const result = [];
  for (let i = 0; i < minLen; i++) {
    result.push(arrays.map(a => a[i]));
  }
  return result;
}
