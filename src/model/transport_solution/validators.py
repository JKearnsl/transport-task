def is_fractional(value: str):
    try:
        numerator, denominator = map(float, value.split('/'))
        result = numerator / denominator
        return isinstance(result, float)
    except (ValueError, TypeError, SyntaxError, AttributeError, ZeroDivisionError):
        return False


def is_float(value: str):
    try:
        float(value)
        return True
    except ValueError:
        return False
