export default function mode(nums) {
  if (nums.length === 0) return [];
  const freq = {};
  for (const n of nums) freq[n] = (freq[n] || 0) + 1;
  const max = Math.max(...Object.values(freq));
  return Object.keys(freq)
    .filter((k) => freq[k] === max)
    .map(Number);
}
