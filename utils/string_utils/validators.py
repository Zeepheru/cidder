import re


def validate_ansi_color_code(string: str) -> bool:
    """Checks whether the supplied string is an ANSI color code.

    Args:
        string (str): String to be validated.

    Returns:
        bool: Whether string is an ANSI color code.
    """

    return re.search(r'\x1b\[[0-9;]+m', string) is not None
