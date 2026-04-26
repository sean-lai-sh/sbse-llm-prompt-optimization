def is_pangram(sentence: str) -> bool:
    return set('abcdefghijklmnopqrstuvwxyz').issubset(set(sentence.lower()))
