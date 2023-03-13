import re


ansi_escape_regex = re.compile(r'\x1b[^m]*m')


def remove_chars(string: str, chars: str = "", replace: str = "") -> str:
    """Removes characters from string."""
    return re.sub(r"["+chars+"]", replace, string)


def remove_ansi_escape_sequences(string):
    return ansi_escape_regex.sub(
        lambda match: match.group() if match.group() == '\x1b[0m' else '', string)
