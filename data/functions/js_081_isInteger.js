export default function isInteger(n) {
  return typeof n === "number" && Number.isFinite(n) && Math.floor(n) === n;
}
