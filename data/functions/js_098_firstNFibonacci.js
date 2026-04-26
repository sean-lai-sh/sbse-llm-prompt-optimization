export default function firstNFibonacci(n) {
  if (n <= 0) return [];
  if (n === 1) return [0];
  const fibs = [0, 1];
  for (let i = 2; i < n; i++) fibs.push(fibs[i - 1] + fibs[i - 2]);
  return fibs;
}
