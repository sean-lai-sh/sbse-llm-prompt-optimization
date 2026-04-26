export default function huffmanCoding(text) {
  const freq = {};
  for (const ch of text) {
    freq[ch] = (freq[ch] || 0) + 1;
  }

  const heap = Object.entries(freq).map(([char, f]) => ({ char, freq: f, left: null, right: null }));
  heap.sort((a, b) => a.freq - b.freq);

  while (heap.length > 1) {
    const left = heap.shift();
    const right = heap.shift();
    const parent = { char: null, freq: left.freq + right.freq, left, right };
    let inserted = false;
    for (let i = 0; i < heap.length; i++) {
      if (parent.freq <= heap[i].freq) {
        heap.splice(i, 0, parent);
        inserted = true;
        break;
      }
    }
    if (!inserted) heap.push(parent);
  }

  const codes = {};
  function buildCodes(node, prefix) {
    if (!node) return;
    if (node.char !== null) {
      codes[node.char] = prefix || '0';
      return;
    }
    buildCodes(node.left, prefix + '0');
    buildCodes(node.right, prefix + '1');
  }

  if (heap.length === 1) buildCodes(heap[0], '');

  const encoded = text.split('').map(ch => codes[ch]).join('');
  return { codes, encoded };
}
