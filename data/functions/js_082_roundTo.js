export default function roundTo(n, decimals) {
  const factor = Math.pow(10, decimals);
  return Math.round(n * factor) / factor;
}
