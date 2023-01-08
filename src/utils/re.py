from re import sub


def remove_chars(string: str, chars: str = "", replace: str = "") -> str:
    """Removes characters from string."""
    return sub(r"["+chars+"]", replace, string)