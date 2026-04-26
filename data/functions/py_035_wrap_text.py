from typing import List


def wrap_text(text: str, width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []
    current_length = 0
    for word in words:
        if current_length + len(word) + (1 if current_line else 0) <= width:
            current_line.append(word)
            current_length += len(word) + (1 if len(current_line) > 1 else 0)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    if current_line:
        lines.append(' '.join(current_line))
    return lines
