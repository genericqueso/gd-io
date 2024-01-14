from typing import Any

# this file is intended to be occupied with methods for translating attributes that can't fit into a lambda expression.
# pretty empty right now but I didn't encounter many attributes that mandated it.

# attribute 41 -> HSV
def decode_hsv(string: str) -> tuple[float | int | bool]:
    args = iter(string.split("a"))  # why this was the separator rob chose, I will never know
    return (
        int(next(args)),  # hue
        float(next(args)),  # saturation
        float(next(args)),  # value
        bool(int(next(args))),  # saturation operation; false if multiplicative, true if additive
        bool(int(next(args))),  # value operation; false if multiplicative, true if additive
    )

def encode_hsv(array: tuple[float | int | bool]) -> str:
    return "a".join(
            [(str(int(entry)) if type(entry) == bool else str(entry)) for entry in array]
        )