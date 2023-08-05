from collections import Counter
from functools import lru_cache


@lru_cache
def count_single_char(text: str, case_insensitive: bool = False) -> int:
    """Returns the number of characters in the string occurring only once. """
    if not isinstance(text, str):
        raise TypeError(f"Error: expected string but got '{type(text).__name__}'")

    if case_insensitive:
        text = text.lower()

    char = Counter(text)
    number_single_char = sum(filter(lambda x: x == 1, char.values()))

    return number_single_char
