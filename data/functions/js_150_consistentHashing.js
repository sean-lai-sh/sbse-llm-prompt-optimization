export default function consistentHashing(nodes, replicas = 100) {
  const ring = new Map();
  const sortedKeys = [];

  function hash(key) {
    let h = 0;
    for (let i = 0; i < key.length; i++) {
      h = (Math.imul(31, h) + key.charCodeAt(i)) | 0;
    }
    return Math.abs(h) % 1000000;
  }

  function addNode(node) {
    for (let i = 0; i < replicas; i++) {
      const vnode = `${node}:${i}`;
      const k = hash(vnode);
      ring.set(k, node);
      const idx = sortedKeys.findIndex(x => x >= k);
      if (idx === -1) sortedKeys.push(k);
      else sortedKeys.splice(idx, 0, k);
    }
  }

  function removeNode(node) {
    for (let i = 0; i < replicas; i++) {
      const k = hash(`${node}:${i}`);
      ring.delete(k);
      const idx = sortedKeys.indexOf(k);
      if (idx !== -1) sortedKeys.splice(idx, 1);
    }
  }

  function getNode(key) {
    if (ring.size === 0) return null;
    const k = hash(key);
    for (const sk of sortedKeys) {
      if (k <= sk) return ring.get(sk);
    }
    return ring.get(sortedKeys[0]);
  }

  for (const node of nodes) addNode(node);

  return { addNode, removeNode, getNode };
}
