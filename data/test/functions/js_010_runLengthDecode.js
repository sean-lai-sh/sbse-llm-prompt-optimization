export default function runLengthDecode(encoded) {
  let out = "";
  let i = 0;
  while (i < encoded.length) {
    let j = i;
    while (j < encoded.length && /\d/.test(encoded[j])) j += 1;
    if (j === i) throw new Error(`expected count at position ${i}`);
    const count = Number(encoded.slice(i, j));
    if (j >= encoded.length) throw new Error("dangling count without character");
    out += encoded[j].repeat(count);
    i = j + 1;
  }
  return out;
}
