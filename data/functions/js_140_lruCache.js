export default function lruCache(capacity, operations) {
  // operations: [{ type: 'get', key } | { type: 'put', key, value }]
  // Returns array of results for 'get' operations (-1 if not found)

  class Node {
    constructor(key, value) {
      this.key = key;
      this.value = value;
      this.prev = null;
      this.next = null;
    }
  }

  class LRUCache {
    constructor(cap) {
      this.capacity = cap;
      this.map = new Map();
      // Sentinel head and tail
      this.head = new Node(0, 0);
      this.tail = new Node(0, 0);
      this.head.next = this.tail;
      this.tail.prev = this.head;
    }

    removeNode(node) {
      node.prev.next = node.next;
      node.next.prev = node.prev;
    }

    addToFront(node) {
      node.next = this.head.next;
      node.prev = this.head;
      this.head.next.prev = node;
      this.head.next = node;
    }

    get(key) {
      if (!this.map.has(key)) return -1;
      const node = this.map.get(key);
      this.removeNode(node);
      this.addToFront(node);
      return node.value;
    }

    put(key, value) {
      if (this.map.has(key)) {
        const node = this.map.get(key);
        node.value = value;
        this.removeNode(node);
        this.addToFront(node);
      } else {
        if (this.map.size === this.capacity) {
          const lru = this.tail.prev;
          this.removeNode(lru);
          this.map.delete(lru.key);
        }
        const newNode = new Node(key, value);
        this.addToFront(newNode);
        this.map.set(key, newNode);
      }
    }

    keys() {
      const result = [];
      let cur = this.head.next;
      while (cur !== this.tail) { result.push(cur.key); cur = cur.next; }
      return result;
    }
  }

  const cache = new LRUCache(capacity);
  const results = [];
  for (const op of operations) {
    if (op.type === "get") {
      results.push({ operation: "get", key: op.key, value: cache.get(op.key) });
    } else if (op.type === "put") {
      cache.put(op.key, op.value);
      results.push({ operation: "put", key: op.key, value: op.value });
    } else if (op.type === "keys") {
      results.push({ operation: "keys", keys: cache.keys() });
    }
  }
  return results;
}
