export default function flattenDeep(arr) {
  const result = [];
  const stack = [...arr];
  while (stack.length > 0) {
    const item = stack.pop();
    if (Array.isArray(item)) {
      stack.push(...item);
    } else {
      result.unshift(item);
    }
  }
  return result;
}
