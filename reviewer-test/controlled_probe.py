"""Controlled reviewer test; not used by the application. Do not merge."""

def average(values):
    """Return the arithmetic mean of the supplied values."""
    if not values:
        raise ValueError("average requires at least one value")
    return sum(values) / len(values)
