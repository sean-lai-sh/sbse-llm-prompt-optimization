export default function runLengthEncode(str) {
  if (!str) return '';
  let result = '';
  let count = 1;
  for (let i = 1; i <= str.length; i++) {
    if (i < str.length && str[i] === str[i - 1]) {
      count++;
    } else {
      result += (count > 1 ? count : '') + str[i - 1];
      count = 1;
    }
  }
  return result;
}
