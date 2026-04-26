import heapq
from typing import Dict, List, Optional, Tuple


def huffman_encode(text: str) -> Tuple[str, Dict[str, str]]:
    if not text:
        return "", {}

    freq: Dict[str, int] = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    if len(freq) == 1:
        ch = list(freq.keys())[0]
        return "0" * len(text), {ch: "0"}

    heap: List[List] = [[count, [ch, ""]] for ch, count in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = "0" + pair[1]
        for pair in hi[1:]:
            pair[1] = "1" + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    codes: Dict[str, str] = {}
    for pair in heap[0][1:]:
        codes[pair[0]] = pair[1]

    encoded = "".join(codes[ch] for ch in text)
    return encoded, codes
