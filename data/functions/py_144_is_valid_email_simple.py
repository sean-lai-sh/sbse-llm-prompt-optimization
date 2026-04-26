def is_valid_email_simple(email: str) -> bool:
    if email.count('@') != 1:
        return False
    local, domain = email.split('@')
    if not local or not domain:
        return False
    if '.' not in domain:
        return False
    parts = domain.split('.')
    if any(len(p) == 0 for p in parts):
        return False
    return True
