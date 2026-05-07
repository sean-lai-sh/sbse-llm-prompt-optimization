export default function singleNumberXor(nums) {
  let acc = 0;
  for (const n of nums) {
    acc ^= n;
  }
  return acc;
}
