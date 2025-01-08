import copy
import logging
import os
from typing import Optional

from concurrent_log_handler import ConcurrentRotatingFileHandler

from ..string_utils.colors import Colors


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
        #TODO should probably be broken down more - split up this long function

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
        self.write_newline_to_logfile(filename=filename)

    def write_newline_to_logfile(self, filename: str) -> None:
        """Writes a new line to the specified log file. Path to log file must exist.

        Args:
            filename (str): Log file to write to. File is relative to the ./logs/directory.
        """

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
    LogConfig().setup(is_debug=True, filename="_TEST_logging.txt")

    # test formatting
    logging.debug("debug")
    logging.info("info")
    logging.warning("warning")
    logging.error("error")
    logging.critical("critical")
