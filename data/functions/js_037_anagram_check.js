export default function anagramCheck(str1, str2) {
  if (str1.length !== str2.length) return false;
  const normalize = s =>
    s.toLowerCase().split('').sort().join('');
  return normalize(str1) === normalize(str2);
}
