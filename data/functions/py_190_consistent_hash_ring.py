import hashlib
from typing import Dict, List, Optional


def consistent_hash_ring(
    nodes: List[str],
    replicas: int,
    requests: List[str],
) -> Dict[str, Optional[str]]:
    ring: Dict[int, str] = {}

    def hash_key(key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(node: str) -> None:
        for i in range(replicas):
            vnode_key = f"{node}:{i}"
            h = hash_key(vnode_key)
            ring[h] = node

    def get_node(key: str) -> Optional[str]:
        if not ring:
            return None
        h = hash_key(key)
        sorted_keys = sorted(ring.keys())
        for k in sorted_keys:
            if h <= k:
                return ring[k]
        return ring[sorted_keys[0]]

    def remove_node(node: str) -> None:
        for i in range(replicas):
            vnode_key = f"{node}:{i}"
            h = hash_key(vnode_key)
            ring.pop(h, None)

    for node in nodes:
        add_node(node)

    results: Dict[str, Optional[str]] = {}
    for req in requests:
        results[req] = get_node(req)
    return results
