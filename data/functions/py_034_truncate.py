def truncate(text: str, max_length: int, ellipsis: str = '...') -> str:
    if len(text) <= max_length:
        return text
    if max_length <= len(ellipsis):
        return ellipsis[:max_length]
    return text[:max_length - len(ellipsis)] + ellipsis
