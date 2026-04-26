def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in card_number.replace(' ', '') if d.isdigit()]
    if len(digits) < 2:
        return False
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            doubled = digit * 2
            total += doubled - 9 if doubled > 9 else doubled
        else:
            total += digit
    return total % 10 == 0
