from collections import Counter
from typing import Optional


def minimum_window_substr(s: str, t: str) -> Optional[str]:
    if not t or not s:
        return None
    need = Counter(t)
    missing = len(t)
    best_start = best_end = -1
    start = 0
    for end, ch in enumerate(s):
        if need.get(ch, 0) > 0:
            missing -= 1
        need[ch] = need.get(ch, 0) - 1
        if missing == 0:
            while need.get(s[start], 0) < 0:
                need[s[start]] = need.get(s[start], 0) + 1
                start += 1
            if best_end == -1 or end - start < best_end - best_start:
                best_start, best_end = start, end
            need[s[start]] = need.get(s[start], 0) + 1
            missing += 1
            start += 1
    return s[best_start:best_end + 1] if best_end != -1 else None
