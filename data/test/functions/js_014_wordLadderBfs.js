export default function wordLadderBfs(begin, end, wordList) {
  const dict = new Set(wordList);
  if (!dict.has(end)) return 0;
  let frontier = new Set([begin]);
  const visited = new Set([begin]);
  let steps = 1;
  while (frontier.size > 0) {
    const next = new Set();
    for (const word of frontier) {
      if (word === end) return steps;
      const chars = word.split("");
      for (let i = 0; i < chars.length; i += 1) {
        const original = chars[i];
        for (let c = 97; c <= 122; c += 1) {
          const candidate = String.fromCharCode(c);
          if (candidate === original) continue;
          chars[i] = candidate;
          const swapped = chars.join("");
          if (dict.has(swapped) && !visited.has(swapped)) {
            visited.add(swapped);
            next.add(swapped);
          }
        }
        chars[i] = original;
      }
    }
    frontier = next;
    steps += 1;
  }
  return 0;
}
