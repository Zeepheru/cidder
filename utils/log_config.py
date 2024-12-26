import copy
import logging
import os
from typing import Optional


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

class LogConfig:
    def setup(self, filename: Optional[str] = None, is_debug: bool = False) -> None:
        """
        sets up the root logger. (Called by `logging.getLogger()`)
        """
        # should probably be broken down more

        self._logger = logging.getLogger()
        logger = self._logger

        # set logging min level
        if is_debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logger.setLevel(level)
        
        mainFormatter = logging.Formatter("[%(asctime)s %(levelname)s]: %(message)s")
        coloredFormatter = ColoredFormatter("[%(asctime)s %(levelname)s]: %(message)s", datefmt="%H:%M:%S")

        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(coloredFormatter)

        # file handler
        # create dir first
        if not os.path.exists("../logs"):
            os.mkdir("../logs")

        if not filename:
            fh = logging.FileHandler("../logs/log.txt", encoding="utf-8")
        else:
            fh = logging.FileHandler(f"../logs/{filename}", encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(mainFormatter)

        # add to Logger
        logger.addHandler(ch)
        logger.addHandler(fh)

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        selected: str
        if record.levelno == logging.CRITICAL:
            selected = Colors.RED
        elif record.levelno == logging.ERROR:
            selected = Colors.ORANGE
        elif record.levelno == logging.WARNING:
            selected = Colors.YELLOW
        elif record.levelno == logging.INFO:
            selected = Colors.RESET
        elif record.levelno == logging.DEBUG:
            selected = Colors.GRAY
        else:
            selected = Colors.PURPLE
        
        new_msg = f"{selected}{record.msg}{Colors.RESET}"

        # create record copy
        temp_record = copy.copy(record)
        temp_record.msg = new_msg

        return logging.Formatter.format(self, temp_record)
    
if __name__ == "__main__":
    
    # setup
    # note that filename is always this random testing file
    LogConfig().setup(is_debug=True, filename="logging-test.txt")

    # test formatting
    logger = logging.debug("debug")
    logger = logging.info("info")
    logger = logging.warning("warning")
    logger = logging.error("error")
    logger = logging.critical("critical")