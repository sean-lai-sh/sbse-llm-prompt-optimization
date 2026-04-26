export default function pipe(...fns) {
  if (fns.length === 0) return x => x;
  return function piped(value) {
    return fns.reduce((acc, fn) => fn(acc), value);
  };
}
