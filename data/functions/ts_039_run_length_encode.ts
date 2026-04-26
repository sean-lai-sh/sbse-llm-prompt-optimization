export function runLengthEncode(s: string): string {
  if (s.length === 0) return "";
  let result = "";
  let count = 1;
  for (let i = 1; i < s.length; i++) {
    if (s[i] === s[i - 1]) {
      count++;
    } else {
      result += (count > 1 ? count : "") + s[i - 1];
      count = 1;
    }
  }
  result += (count > 1 ? count : "") + s[s.length - 1];
  return result;
}
