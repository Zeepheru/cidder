import copy
import logging
import os
from typing import Optional

from concurrent_log_handler import ConcurrentRotatingFileHandler


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
    """Class that handles configuration for Python's `Logging`.
    """
    def __init__(self) -> None:
        self._logger: logging.Logger

    def setup(self, filename: Optional[str] = None, is_debug: bool = False) -> None:
        """Sets up the root logger, which can be called by `logging.getLogger()`

        Args:
            filename (Optional[str], optional): _description_. Defaults to None.
            is_debug (bool, optional): _description_. Defaults to False.
        """        """sets up the root logger. (Called by `logging.getLogger()`)
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

        main_formatter = logging.Formatter("[%(asctime)s %(levelname)s]: %(message)s")
        colored_formatter = ColoredFormatter(
            "[%(asctime)s %(levelname)s]: %(message)s", datefmt="%H:%M:%S")

        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(colored_formatter)

        # file handler
        # create dir first
        if not os.path.exists("./logs"):
            os.mkdir("./logs")

        if not filename:
            filename = "log.txt"

        fh = ConcurrentRotatingFileHandler(
            f"./logs/{filename}",
            "a", maxBytes=20*1024*1024, backupCount=5) # 10MB, 5 backups

        fh.setLevel(level)
        fh.setFormatter(main_formatter)

        # add to Logger
        logger.addHandler(ch)
        logger.addHandler(fh)

        # add a new line to the log file
        with open(f"./logs/{filename}", "a", encoding="utf-8") as f:
            f.write(
                "-------------------------------------------------------"
                + "-----------------------------------------------------------------\n")
            f.close()

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
    logging.debug("debug")
    logging.info("info")
    logging.warning("warning")
    logging.error("error")
    logging.critical("critical")
