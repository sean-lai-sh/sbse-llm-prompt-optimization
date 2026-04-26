export default function balancedBrackets(str) {
  const stack = [];
  const matching = { ')': '(', ']': '[', '}': '{' };
  const closing = new Set([')', ']', '}']);
  const opening = new Set(['(', '[', '{']);

  for (const ch of str) {
    if (opening.has(ch)) {
      stack.push(ch);
    } else if (closing.has(ch)) {
      if (stack.length === 0 || stack[stack.length - 1] !== matching[ch]) {
        return false;
      }
      stack.pop();
    }
  }
  return stack.length === 0;
}
