from typing import Optional, Union


def safe_divide(
    numerator: Union[int, float],
    denominator: Union[int, float],
    default: Optional[float] = None,
    raise_on_zero: bool = False,
    precision: Optional[int] = None
) -> Optional[float]:
    if not isinstance(numerator, (int, float)):
        raise TypeError(f"numerator must be numeric, got {type(numerator).__name__}")
    if not isinstance(denominator, (int, float)):
        raise TypeError(f"denominator must be numeric, got {type(denominator).__name__}")

    import math
    if math.isnan(numerator) or math.isnan(denominator):
        if raise_on_zero:
            raise ValueError("NaN values are not allowed")
        return default

    if math.isinf(denominator):
        return 0.0

    if denominator == 0:
        if raise_on_zero:
            raise ZeroDivisionError("Division by zero is not allowed")
        return default

    result = numerator / denominator

    if math.isinf(result):
        if raise_on_zero:
            raise OverflowError("Result is infinite")
        return default

    if precision is not None:
        result = round(result, precision)

    return result
