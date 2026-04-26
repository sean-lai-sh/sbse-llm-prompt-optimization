export default function lcm(a, b) {
  let g = a;
  let temp = b;
  while (temp !== 0) {
    [g, temp] = [temp, g % temp];
  }
  return Math.abs(a * b) / g;
}
