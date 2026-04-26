def longest_palindrome_substr(s: str) -> str:
    if not s:
        return ""
    start, end = 0, 0
    for i in range(len(s)):
        for lo, hi in [(i, i), (i, i + 1)]:
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                if hi - lo > end - start:
                    start, end = lo, hi
                lo -= 1
                hi += 1
    return s[start:end + 1]
