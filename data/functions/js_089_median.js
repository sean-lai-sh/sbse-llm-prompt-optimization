export default function median(sortedNums) {
  const len = sortedNums.length;
  if (len === 0) return undefined;
  const mid = Math.floor(len / 2);
  return len % 2 !== 0 ? sortedNums[mid] : (sortedNums[mid - 1] + sortedNums[mid]) / 2;
}
