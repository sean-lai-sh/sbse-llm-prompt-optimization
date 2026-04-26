def is_rotation(s1: str, s2: str) -> bool:
    if len(s1) != len(s2):
        return False
    if not s1:
        return True
    doubled = s1 + s1
    return s2 in doubled
