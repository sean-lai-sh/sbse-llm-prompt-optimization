export default function wordFrequency(str) {
  const words = str.toLowerCase().match(/\b\w+\b/g) || [];
  const freq = {};
  for (const word of words) {
    freq[word] = (freq[word] || 0) + 1;
  }
  return freq;
}
