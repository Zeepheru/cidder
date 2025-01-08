
import logging

from cidderbot.utils.string_utils.validators import validate_ansi_color_code


class Colors:
    """ 
    ANSI color codes. 
    Credit to https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007

    For 256 colors https://gist.github.com/JBlond/2fea43a3049b38287e5e9cefc87b2124
    """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    ORANGE = "\033[38;5;202m"
    GRAY = "\033[38;5;234m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    RESET = "\033[0m"

    # cancel SGR codes if we don't write to a terminal
    if not __import__("sys").stdout.isatty():
        for _ in dir():
            if isinstance(_, str) and _[0] != "_":
                locals()[_] = ""
    else:
        # set Windows console in VT mode
        if __import__("platform").system() == "Windows":
            kernel32 = __import__("ctypes").windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            del kernel32

def colorize_string(string: str, color_code: str) -> str:
    """Colorizes given string with given color code, applying the appropriate ANSI escape codes.
    If the supplied color code is invalid, the string will not be formatted.

    Args:
        string (str): String to be colored.
        color (str): ANSI escape code for color.
    
    Returns:
        str: Colorised string.
    """
    # print(f"CODE: {color_code}, validation: {validate_ansi_color_code(color_code)}")
    if validate_ansi_color_code(color_code):
        return f"{color_code}{string}{Colors.RESET}"

    if not __import__("sys").stdout.isatty():
        # Not a terminal!
        return string

    logging.warning("Supplied color code %s is not valid.", color_code)
    return string
