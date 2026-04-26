from typing import List, Optional, Set


def word_break(
    s: str,
    word_dict: List[str],
    return_sentences: bool = False
) -> bool | List[str]:
    if not s:
        return [] if return_sentences else False

    word_set: Set[str] = set(word_dict)
    n = len(s)

    if not return_sentences:
        dp = [False] * (n + 1)
        dp[0] = True
        for i in range(1, n + 1):
            for j in range(i):
                if dp[j] and s[j:i] in word_set:
                    dp[i] = True
                    break
        return dp[n]

    def backtrack(start: int, path: List[str]) -> List[str]:
        if start == n:
            return [' '.join(path)]
        results: List[str] = []
        for end in range(start + 1, n + 1):
            word = s[start:end]
            if word in word_set:
                path.append(word)
                results.extend(backtrack(end, path))
                path.pop()
        return results

    return backtrack(0, [])
