def most_frequent_char(s: str) -> str:
    if not s:
        return ""
    freq: dict = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    return max(freq, key=lambda k: freq[k])
