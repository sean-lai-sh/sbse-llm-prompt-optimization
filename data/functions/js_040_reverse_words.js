export default function reverseWords(str) {
  return str
    .trim()
    .split(/\s+/)
    .reverse()
    .join(' ');
}
