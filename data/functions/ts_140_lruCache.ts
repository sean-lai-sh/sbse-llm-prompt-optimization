interface LRUCache<K, V> {
  get: (key: K) => V | undefined;
  put: (key: K, value: V) => void;
  size: () => number;
}

interface DLinkedNode<K, V> {
  key: K;
  value: V;
  prev: DLinkedNode<K, V> | null;
  next: DLinkedNode<K, V> | null;
}

export function lruCache<K, V>(capacity: number): LRUCache<K, V> {
  const map = new Map<K, DLinkedNode<K, V>>();

  // Dummy head and tail sentinels
  const head: DLinkedNode<K, V> = { key: null as unknown as K, value: null as unknown as V, prev: null, next: null };
  const tail: DLinkedNode<K, V> = { key: null as unknown as K, value: null as unknown as V, prev: null, next: null };
  head.next = tail;
  tail.prev = head;

  const removeNode = (node: DLinkedNode<K, V>): void => {
    node.prev!.next = node.next;
    node.next!.prev = node.prev;
  };

  const addToFront = (node: DLinkedNode<K, V>): void => {
    node.next = head.next;
    node.prev = head;
    head.next!.prev = node;
    head.next = node;
  };

  const get = (key: K): V | undefined => {
    const node = map.get(key);
    if (!node) return undefined;
    removeNode(node);
    addToFront(node);
    return node.value;
  };

  const put = (key: K, value: V): void => {
    if (map.has(key)) {
      const node = map.get(key)!;
      node.value = value;
      removeNode(node);
      addToFront(node);
    } else {
      if (map.size >= capacity) {
        const lruNode = tail.prev!;
        removeNode(lruNode);
        map.delete(lruNode.key);
      }
      const newNode: DLinkedNode<K, V> = { key, value, prev: null, next: null };
      addToFront(newNode);
      map.set(key, newNode);
    }
  };

  const size = (): number => map.size;

  return { get, put, size };
}
