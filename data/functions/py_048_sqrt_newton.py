def sqrt_newton(n: float, tolerance: float = 1e-10) -> float:
    if n < 0:
        raise ValueError("Cannot compute square root of a negative number")
    if n == 0:
        return 0.0
    x = float(n)
    while True:
        x_new = (x + n / x) / 2.0
        if abs(x_new - x) < tolerance:
            return x_new
        x = x_new
