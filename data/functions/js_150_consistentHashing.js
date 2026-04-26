export default function consistentHashing(operations, virtualNodes = 150) {
  // Consistent hashing ring for distributed key-value routing
  // operations: [{ type: 'addNode'|'removeNode'|'getNode'|'getKeyDistribution', id }]
  // Returns results array

  // FNV-1a inspired deterministic hash function
  function hash(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
      h = h >>> 0; // ensure unsigned 32-bit
    }
    return h;
  }

  class ConsistentHashRing {
    constructor(vnodes) {
      this.vnodes = vnodes;
      this.ring = new Map(); // position -> nodeId
      this.sortedPositions = [];
      this.nodes = new Set();
    }

    addNode(nodeId) {
      if (this.nodes.has(nodeId)) return false;
      this.nodes.add(nodeId);
      for (let i = 0; i < this.vnodes; i++) {
        const vKey = `${nodeId}:vnode:${i}`;
        const pos = hash(vKey);
        this.ring.set(pos, nodeId);
        this.sortedPositions.push(pos);
      }
      this.sortedPositions.sort((a, b) => a - b);
      return true;
    }

    removeNode(nodeId) {
      if (!this.nodes.has(nodeId)) return false;
      this.nodes.delete(nodeId);
      for (let i = 0; i < this.vnodes; i++) {
        const vKey = `${nodeId}:vnode:${i}`;
        const pos = hash(vKey);
        this.ring.delete(pos);
      }
      this.sortedPositions = this.sortedPositions.filter((p) => this.ring.has(p));
      return true;
    }

    getNode(key) {
      if (this.ring.size === 0) return null;
      const keyHash = hash(key);
      // Binary search for first position >= keyHash
      let lo = 0, hi = this.sortedPositions.length;
      while (lo < hi) {
        const mid = (lo + hi) >>> 1;
        if (this.sortedPositions[mid] < keyHash) lo = mid + 1;
        else hi = mid;
      }
      // Wrap around to first node if past the end
      const pos = this.sortedPositions[lo % this.sortedPositions.length];
      return this.ring.get(pos);
    }

    getKeyDistribution(keys) {
      const distribution = {};
      for (const nodeId of this.nodes) distribution[nodeId] = 0;
      for (const key of keys) {
        const node = this.getNode(key);
        if (node) distribution[node] = (distribution[node] || 0) + 1;
      }
      return distribution;
    }

    getNodeCount() {
      return this.nodes.size;
    }

    getRingSize() {
      return this.ring.size;
    }

    getNeighbors(nodeId, k = 1) {
      // Get k successor nodes for replication purposes
      const replicas = new Set();
      const start = hash(`${nodeId}:vnode:0`) >>> 0;
      let lo = 0, hi = this.sortedPositions.length;
      while (lo < hi) {
        const mid = (lo + hi) >>> 1;
        if (this.sortedPositions[mid] < start) lo = mid + 1;
        else hi = mid;
      }
      let idx = lo % this.sortedPositions.length;
      let checked = 0;
      while (replicas.size < k && checked < this.sortedPositions.length) {
        const owner = this.ring.get(this.sortedPositions[idx]);
        if (owner && owner !== nodeId) replicas.add(owner);
        idx = (idx + 1) % this.sortedPositions.length;
        checked++;
      }
      return [...replicas];
    }
  }

  const ring = new ConsistentHashRing(virtualNodes);
  const results = [];

  for (const op of operations) {
    if (op.type === "addNode") {
      const added = ring.addNode(op.id);
      results.push({ operation: "addNode", id: op.id, added, ringSize: ring.getRingSize() });
    } else if (op.type === "removeNode") {
      const removed = ring.removeNode(op.id);
      results.push({ operation: "removeNode", id: op.id, removed, ringSize: ring.getRingSize() });
    } else if (op.type === "getNode") {
      results.push({ operation: "getNode", key: op.id, node: ring.getNode(op.id) });
    } else if (op.type === "getKeyDistribution") {
      results.push({
        operation: "getKeyDistribution",
        distribution: ring.getKeyDistribution(op.keys || []),
      });
    } else if (op.type === "getNeighbors") {
      results.push({
        operation: "getNeighbors",
        id: op.id,
        neighbors: ring.getNeighbors(op.id, op.k || 1),
      });
    } else if (op.type === "nodeCount") {
      results.push({ operation: "nodeCount", count: ring.getNodeCount() });
    }
  }

  return results;
}
