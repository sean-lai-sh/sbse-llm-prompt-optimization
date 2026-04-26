interface HuffmanNode {
  char: string | null;
  freq: number;
  left: HuffmanNode | null;
  right: HuffmanNode | null;
}

interface HuffmanResult {
  codes: Map<string, string>;
  encoded: string;
  tree: HuffmanNode | null;
}

export function huffmanCoding(text: string): HuffmanResult {
  if (text.length === 0) return { codes: new Map(), encoded: "", tree: null };

  // Build frequency map
  const freq = new Map<string, number>();
  for (const ch of text) freq.set(ch, (freq.get(ch) ?? 0) + 1);

  // Min-heap using sorted array for simplicity
  const nodes: HuffmanNode[] = Array.from(freq.entries()).map(([char, f]) => ({
    char,
    freq: f,
    left: null,
    right: null,
  }));

  nodes.sort((a, b) => a.freq - b.freq);

  // Build Huffman tree
  while (nodes.length > 1) {
    const left = nodes.shift()!;
    const right = nodes.shift()!;
    const merged: HuffmanNode = {
      char: null,
      freq: left.freq + right.freq,
      left,
      right,
    };
    // Insert in sorted position
    let inserted = false;
    for (let i = 0; i < nodes.length; i++) {
      if (merged.freq <= nodes[i].freq) {
        nodes.splice(i, 0, merged);
        inserted = true;
        break;
      }
    }
    if (!inserted) nodes.push(merged);
  }

  const tree = nodes[0] ?? null;
  const codes = new Map<string, string>();

  // Generate codes via DFS
  const buildCodes = (node: HuffmanNode | null, code: string): void => {
    if (!node) return;
    if (node.char !== null) {
      codes.set(node.char, code || "0"); // single char edge case
      return;
    }
    buildCodes(node.left, code + "0");
    buildCodes(node.right, code + "1");
  };

  buildCodes(tree, "");

  const encoded = text.split("").map((ch) => codes.get(ch) ?? "").join("");

  return { codes, encoded, tree };
}
