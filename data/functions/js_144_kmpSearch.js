export default function kmpSearch(text, pattern) {
  // Knuth-Morris-Pratt string search algorithm
  // Returns all starting indices where pattern occurs in text
  if (!pattern || pattern.length === 0) return [];
  if (!text || text.length === 0) return [];
  if (pattern.length > text.length) return [];

  // Build longest proper prefix-suffix (LPS) array
  function buildLPS(pat) {
    const lps = new Array(pat.length).fill(0);
    let len = 0;
    let i = 1;
    while (i < pat.length) {
      if (pat[i] === pat[len]) {
        lps[i++] = ++len;
      } else if (len > 0) {
        len = lps[len - 1];
      } else {
        lps[i++] = 0;
      }
    }
    return lps;
  }

  const lps = buildLPS(pattern);
  const matches = [];
  let ti = 0; // text index
  let pi = 0; // pattern index

  while (ti < text.length) {
    if (text[ti] === pattern[pi]) {
      ti++;
      pi++;
    }
    if (pi === pattern.length) {
      matches.push(ti - pi);
      pi = lps[pi - 1];
    } else if (ti < text.length && text[ti] !== pattern[pi]) {
      if (pi !== 0) {
        pi = lps[pi - 1];
      } else {
        ti++;
      }
    }
  }

  return matches;
}
