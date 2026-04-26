def count_substrings(s: str, sub: str) -> int:
    if not sub:
        return 0
    count = 0
    start = 0
    while True:
        pos = s.find(sub, start)
        if pos == -1:
            break
        count += 1
        start = pos + 1
    return count
