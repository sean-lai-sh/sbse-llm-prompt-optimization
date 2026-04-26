import re
from typing import Dict, List, Optional, Tuple


def regex_tokenizer(
    text: str,
    patterns: Optional[Dict[str, str]] = None,
    case_sensitive: bool = True,
    skip_whitespace: bool = True,
    raise_on_unknown: bool = False
) -> List[Tuple[str, str]]:
    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text).__name__}")

    default_patterns: Dict[str, str] = {
        'FLOAT': r'\d+\.\d+',
        'INTEGER': r'\d+',
        'STRING': r'"[^"]*"|\'[^\']*\'',
        'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
        'OPERATOR': r'[+\-*/%=<>!&|^~]+',
        'PUNCTUATION': r'[()[\]{},.:;]',
        'WHITESPACE': r'\s+',
        'NEWLINE': r'\n',
    }

    active_patterns = patterns if patterns is not None else default_patterns

    flags = 0 if case_sensitive else re.IGNORECASE

    combined_parts = []
    token_names = []
    for name, pattern in active_patterns.items():
        try:
            re.compile(pattern, flags)
        except re.error as exc:
            raise ValueError(f"Invalid pattern for token '{name}': {exc}") from exc
        combined_parts.append(f'(?P<{re.escape(name) if not name.isidentifier() else name}>{pattern})')
        token_names.append(name)

    combined = '|'.join(combined_parts)

    try:
        master_re = re.compile(combined, flags)
    except re.error as exc:
        raise ValueError(f"Failed to compile combined pattern: {exc}") from exc

    tokens: List[Tuple[str, str]] = []
    pos = 0
    n = len(text)

    while pos < n:
        match = master_re.match(text, pos)
        if match is None:
            if raise_on_unknown:
                raise ValueError(f"Unrecognized token at position {pos}: {text[pos:pos + 10]!r}")
            tokens.append(('UNKNOWN', text[pos]))
            pos += 1
            continue

        kind = match.lastgroup
        value = match.group()

        if skip_whitespace and kind in ('WHITESPACE', 'NEWLINE'):
            pos = match.end()
            continue

        tokens.append((kind, value))  # type: ignore[arg-type]
        pos = match.end()

    return tokens
