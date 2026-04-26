interface UnionFind {
  find: (x: number) => number;
  union: (x: number, y: number) => boolean;
  connected: (x: number, y: number) => boolean;
  componentCount: () => number;
}

export function unionFind(n: number): UnionFind {
  const parent: number[] = Array.from({ length: n }, (_, i) => i);
  const rank: number[] = new Array(n).fill(0);
  let components = n;

  const find = (x: number): number => {
    if (parent[x] !== x) {
      parent[x] = find(parent[x]); // path compression
    }
    return parent[x];
  };

  const union = (x: number, y: number): boolean => {
    const rootX = find(x);
    const rootY = find(y);
    if (rootX === rootY) return false; // already connected

    // Union by rank
    if (rank[rootX] < rank[rootY]) {
      parent[rootX] = rootY;
    } else if (rank[rootX] > rank[rootY]) {
      parent[rootY] = rootX;
    } else {
      parent[rootY] = rootX;
      rank[rootX]++;
    }
    components--;
    return true;
  };

  const connected = (x: number, y: number): boolean => find(x) === find(y);

  const componentCount = (): number => components;

  return { find, union, connected, componentCount };
}
