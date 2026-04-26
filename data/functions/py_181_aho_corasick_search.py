from collections import deque
from typing import Dict, List, Optional


def aho_corasick_search(text: str, patterns: List[str]) -> Dict[str, List[int]]:
    goto: List[Dict[str, int]] = [{}]
    fail: List[int] = [0]
    output: List[List[str]] = [[]]
    state_count = 0

    for pattern in patterns:
        cur = 0
        for ch in pattern:
            if ch not in goto[cur]:
                state_count += 1
                goto.append({})
                fail.append(0)
                output.append([])
                goto[cur][ch] = state_count
            cur = goto[cur][ch]
        output[cur].append(pattern)

    queue: deque = deque()
    for ch, s in goto[0].items():
        fail[s] = 0
        queue.append(s)

    while queue:
        r = queue.popleft()
        for ch, s in goto[r].items():
            queue.append(s)
            state = fail[r]
            while state != 0 and ch not in goto[state]:
                state = fail[state]
            fail[s] = goto[state].get(ch, 0)
            if fail[s] == s:
                fail[s] = 0
            output[s] = output[s] + output[fail[s]]

    results: Dict[str, List[int]] = {p: [] for p in patterns}
    cur = 0
    for i, ch in enumerate(text):
        while cur != 0 and ch not in goto[cur]:
            cur = fail[cur]
        cur = goto[cur].get(ch, 0)
        for pattern in output[cur]:
            start = i - len(pattern) + 1
            results[pattern].append(start)

    return results
