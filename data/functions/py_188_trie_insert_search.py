from typing import Dict, List, Optional, Tuple


def trie_insert_search(
    words: List[str], queries: List[Tuple[str, str]]
) -> List[bool]:
    class TrieNode:
        def __init__(self) -> None:
            self.children: Dict[str, "TrieNode"] = {}
            self.is_end = False

    root = TrieNode()

    def insert(word: str) -> None:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(word: str) -> bool:
        node = root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(prefix: str) -> bool:
        node = root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def delete(word: str) -> bool:
        path: List[Tuple[TrieNode, str]] = []
        node = root
        for ch in word:
            if ch not in node.children:
                return False
            path.append((node, ch))
            node = node.children[ch]
        if not node.is_end:
            return False
        node.is_end = False
        for parent, ch in reversed(path):
            child = parent.children[ch]
            if not child.children and not child.is_end:
                del parent.children[ch]
            else:
                break
        return True

    for word in words:
        insert(word)

    results = []
    for op, val in queries:
        if op == "search":
            results.append(search(val))
        elif op == "prefix":
            results.append(starts_with(val))
        elif op == "delete":
            results.append(delete(val))
    return results
