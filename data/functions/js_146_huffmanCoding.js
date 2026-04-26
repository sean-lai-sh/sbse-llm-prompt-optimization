export default function huffmanCoding(text) {
  // Huffman encoding and decoding
  // Returns { codes, encoded, decode(bits) }

  if (!text || text.length === 0) return { codes: {}, encoded: "", decode: () => "" };

  // Count character frequencies
  const freq = {};
  for (const ch of text) {
    freq[ch] = (freq[ch] || 0) + 1;
  }

  const chars = Object.keys(freq);

  // Special case: single unique character
  if (chars.length === 1) {
    const codes = { [chars[0]]: "0" };
    const encoded = text.split("").map(() => "0").join("");
    const decode = (bits) => chars[0].repeat(bits.length);
    return { codes, encoded, decode };
  }

  // Build min-heap manually (sorted list as priority queue)
  let nodes = chars.map((ch) => ({ char: ch, freq: freq[ch], left: null, right: null }));
  nodes.sort((a, b) => a.freq - b.freq);

  // Build Huffman tree
  while (nodes.length > 1) {
    const left = nodes.shift();
    const right = nodes.shift();
    const parent = { char: null, freq: left.freq + right.freq, left, right };
    // Insert in sorted position
    let inserted = false;
    for (let i = 0; i < nodes.length; i++) {
      if (parent.freq <= nodes[i].freq) {
        nodes.splice(i, 0, parent);
        inserted = true;
        break;
      }
    }
    if (!inserted) nodes.push(parent);
  }

  const root = nodes[0];
  const codes = {};

  // Traverse tree to build codes
  function buildCodes(node, prefix) {
    if (!node) return;
    if (node.char !== null) {
      codes[node.char] = prefix || "0";
      return;
    }
    buildCodes(node.left, prefix + "0");
    buildCodes(node.right, prefix + "1");
  }
  buildCodes(root, "");

  // Encode text
  const encoded = text.split("").map((ch) => codes[ch]).join("");

  // Decode bits back to text
  function decode(bits) {
    if (!bits || bits.length === 0) return "";
    let result = "";
    let node = root;
    for (const bit of bits) {
      node = bit === "0" ? node.left : node.right;
      if (node.char !== null) {
        result += node.char;
        node = root;
      }
    }
    return result;
  }

  // Compute compression ratio
  const originalBits = text.length * 8;
  const compressedBits = encoded.length;
  const ratio = originalBits > 0 ? compressedBits / originalBits : 1;

  return { codes, encoded, decode, ratio, freq };
}
