export default function sumOfDigits(n) {
  return String(Math.abs(n))
    .split("")
    .reduce((sum, d) => sum + Number(d), 0);
}
