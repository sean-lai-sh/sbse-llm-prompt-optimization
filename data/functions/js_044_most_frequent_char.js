export default function mostFrequentChar(str) {
  if (!str) return null;
  const freq = {};
  for (const ch of str) {
    freq[ch] = (freq[ch] || 0) + 1;
  }
  let maxChar = null;
  let maxCount = 0;
  for (const [ch, count] of Object.entries(freq)) {
    if (count > maxCount) {
      maxCount = count;
      maxChar = ch;
    }
  }
  return maxChar;
}
