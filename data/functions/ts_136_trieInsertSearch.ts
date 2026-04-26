interface TrieNode {
  children: Map<string, TrieNode>;
  isEndOfWord: boolean;
}

interface Trie {
  root: TrieNode;
  insert: (word: string) => void;
  search: (word: string) => boolean;
  startsWith: (prefix: string) => boolean;
}

function createTrieNode(): TrieNode {
  return { children: new Map(), isEndOfWord: false };
}

export function trieInsertSearch(words: string[]): Trie {
  const root = createTrieNode();

  const insert = (word: string): void => {
    let node = root;
    for (const ch of word) {
      if (!node.children.has(ch)) {
        node.children.set(ch, createTrieNode());
      }
      node = node.children.get(ch)!;
    }
    node.isEndOfWord = true;
  };

  const search = (word: string): boolean => {
    let node = root;
    for (const ch of word) {
      if (!node.children.has(ch)) return false;
      node = node.children.get(ch)!;
    }
    return node.isEndOfWord;
  };

  const startsWith = (prefix: string): boolean => {
    let node = root;
    for (const ch of prefix) {
      if (!node.children.has(ch)) return false;
      node = node.children.get(ch)!;
    }
    return true;
  };

  for (const word of words) insert(word);

  return { root, insert, search, startsWith };
}
