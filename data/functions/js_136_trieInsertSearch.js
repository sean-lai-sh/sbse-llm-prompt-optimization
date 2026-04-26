export default function trieInsertSearch(operations) {
  // operations: [{ type: 'insert'|'search'|'startsWith', word }]
  // Returns results array for 'search' and 'startsWith' operations

  class TrieNode {
    constructor() {
      this.children = {};
      this.isEnd = false;
    }
  }

  class Trie {
    constructor() {
      this.root = new TrieNode();
    }

    insert(word) {
      let node = this.root;
      for (const ch of word) {
        if (!node.children[ch]) node.children[ch] = new TrieNode();
        node = node.children[ch];
      }
      node.isEnd = true;
    }

    search(word) {
      let node = this.root;
      for (const ch of word) {
        if (!node.children[ch]) return false;
        node = node.children[ch];
      }
      return node.isEnd;
    }

    startsWith(prefix) {
      let node = this.root;
      for (const ch of prefix) {
        if (!node.children[ch]) return false;
        node = node.children[ch];
      }
      return true;
    }

    getAllWithPrefix(prefix) {
      let node = this.root;
      for (const ch of prefix) {
        if (!node.children[ch]) return [];
        node = node.children[ch];
      }
      const results = [];
      const dfs = (n, current) => {
        if (n.isEnd) results.push(prefix.slice(0, prefix.length - current.length) + current.split("").reverse().join(""));
        for (const [ch, child] of Object.entries(n.children)) dfs(child, current + ch);
      };
      const collectWords = (n, built) => {
        if (n.isEnd) results.push(built);
        for (const [ch, child] of Object.entries(n.children)) collectWords(child, built + ch);
      };
      collectWords(node, prefix);
      return results;
    }

    delete(word) {
      const deleteHelper = (node, word, depth) => {
        if (!node) return false;
        if (depth === word.length) {
          if (!node.isEnd) return false;
          node.isEnd = false;
          return Object.keys(node.children).length === 0;
        }
        const ch = word[depth];
        if (!node.children[ch]) return false;
        const shouldDelete = deleteHelper(node.children[ch], word, depth + 1);
        if (shouldDelete) {
          delete node.children[ch];
          return !node.isEnd && Object.keys(node.children).length === 0;
        }
        return false;
      };
      deleteHelper(this.root, word, 0);
    }
  }

  const trie = new Trie();
  const results = [];
  for (const op of operations) {
    if (op.type === "insert") {
      trie.insert(op.word);
    } else if (op.type === "search") {
      results.push({ operation: "search", word: op.word, result: trie.search(op.word) });
    } else if (op.type === "startsWith") {
      results.push({ operation: "startsWith", prefix: op.word, result: trie.startsWith(op.word) });
    } else if (op.type === "delete") {
      trie.delete(op.word);
    } else if (op.type === "getAllWithPrefix") {
      results.push({ operation: "getAllWithPrefix", prefix: op.word, result: trie.getAllWithPrefix(op.word) });
    }
  }
  return results;
}
