export default function digitCount(n) {
  return String(Math.abs(n)).replace(".", "").length;
}
