from typing import Dict


def word_count(text: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for word in text.lower().split():
        cleaned = ''.join(c for c in word if c.isalnum())
        if cleaned:
            counts[cleaned] = counts.get(cleaned, 0) + 1
    return counts
