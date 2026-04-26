from collections import Counter


def is_anagram(s1: str, s2: str) -> bool:
    return Counter(s1.lower().replace(' ', '')) == Counter(s2.lower().replace(' ', ''))
