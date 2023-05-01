
def from_fraction_to_float(value: str):
    numerator, denominator = map(float, value.split('/'))
    return float(numerator / denominator)
