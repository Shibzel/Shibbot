import re


def remove_chars(string: str, chars: str = "", replace: str = "") -> str:
    """Removes characters from string."""
    return re.sub(r"["+chars+"]", replace, string)