"""Basic functions."""
import re


def endswith(text: str, word: str) -> bool:
    """Verifies if the sentence ends with `word` excluding some special characters."""
    text = text.lower()
    while True:
        if text.endswith(word):
            return True
        elif text.endswith(("?", "!", ".", "-", ":", ",", "^", "~", "*", ";", " ", "\"")):
            text = text[:len(text)-1]
        else:
            return False


def filter_doubles(_list: list) -> list:
    """Return the list without doubles of the same object."""
    filtered = []
    for obj in _list:
        if obj not in filtered:
            filtered.append(obj)
    return filtered


def remove_chars(string: str, chars: str = "", replace: str = "") -> str:
    """Removes characters from string"""
    return re.sub(r"["+chars+"]", replace, string)
