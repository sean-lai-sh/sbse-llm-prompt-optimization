from typing import Dict


def word_frequency(s: str) -> Dict[str, int]:
    freq: Dict[str, int] = {}
    for word in s.lower().split():
        freq[word] = freq.get(word, 0) + 1
    return freq
