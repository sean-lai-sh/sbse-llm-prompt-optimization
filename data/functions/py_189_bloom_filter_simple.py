import hashlib
import math
from typing import List


def bloom_filter_simple(
    items: List[str], queries: List[str], false_positive_rate: float = 0.01
) -> List[bool]:
    n = max(len(items), 1)
    m = math.ceil(-n * math.log(false_positive_rate) / (math.log(2) ** 2))
    k = max(1, round((m / n) * math.log(2)))
    bit_array = [False] * m

    def get_hash_positions(item: str) -> List[int]:
        positions = []
        for seed in range(k):
            h = hashlib.md5(f"{seed}:{item}".encode()).hexdigest()
            positions.append(int(h, 16) % m)
        return positions

    for item in items:
        for pos in get_hash_positions(item):
            bit_array[pos] = True

    results = []
    for query in queries:
        positions = get_hash_positions(query)
        results.append(all(bit_array[pos] for pos in positions))
    return results
