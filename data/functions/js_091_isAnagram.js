export default function isAnagram(a, b) {
  const normalize = (s) => s.toLowerCase().split("").sort().join("");
  return normalize(a) === normalize(b);
}
