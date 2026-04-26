export default function minArray(arr) {
  return arr.reduce((min, n) => (n < min ? n : min), arr[0]);
}
