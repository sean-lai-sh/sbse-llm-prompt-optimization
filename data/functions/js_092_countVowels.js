export default function countVowels(str) {
  return (str.match(/[aeiou]/gi) || []).length;
}
