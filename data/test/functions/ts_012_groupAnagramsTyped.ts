export function groupAnagramsTyped(words: string[]): string[][] {
  const buckets = new Map<string, string[]>();
  for (const word of words) {
    const key = word.split("").sort().join("");
    const list = buckets.get(key);
    if (list) list.push(word);
    else buckets.set(key, [word]);
  }
  return Array.from(buckets.values());
}
