export function balancedBrackets(s: string): boolean {
  const stack: string[] = [];
  const matching: Record<string, string> = { ")": "(", "]": "[", "}": "{" };
  const closing = new Set([")", "]", "}"]);
  const opening = new Set(["(", "[", "{"]);

  for (const ch of s) {
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
