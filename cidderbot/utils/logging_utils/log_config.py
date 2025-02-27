import logging
import os
import re
from typing import Optional

import discord
from concurrent_log_handler import ConcurrentRotatingFileHandler

from cidderbot.utils.string_utils.colors import Colors, colorize_string

LOG_LEVEL_COLORS = {
    logging.CRITICAL: Colors.RED,
    logging.ERROR: Colors.ORANGE,
    logging.WARNING: Colors.YELLOW,
    logging.INFO: Colors.RESET,
    logging.DEBUG: Colors.GRAY,
}


class LogConfig:
    """Class that handles configuration for Python's `Logging`."""

    LOG_PATH = "logs"
    DEFAULT_LOG_FILE = "cidder.log"
    DEFAULT_DISCORD_SUFFIX = "_discord"
    DEFAULT_PLAINTEXT_SUFFIX = "_plaintext"

    def __init__(self) -> None:
        self._logger: logging.Logger

        # this is needed because I need to get this handler later
        self.discord_handler = None

    def setup(self, filename: Optional[str] = None, is_debug: bool = False) -> None:
        """Sets up the discord logger, used internally by the discord Python module, and
        the root logger, which can be called by `logging.getLogger()`

        A total of 3 log files are created:
        - cidder.log: main logger (level), discord (WARNING)
        - cidder_plaintext.log: main logger (level), discord (WARNING) - but with no color/ANSI formatting
        - cidder_discord.log: discord (level)

        Note: in a running environment that is not attached to a terminal, all colored outputs are disabled.

        Args:
            filename (Optional[str], optional): _description_. Defaults to None.
            is_debug (bool, optional): _description_. Defaults to False.
        """

        # set logging min level
        if is_debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logger = self._get_main_logger(level)
        logger_discord = self._get_discord_logger(level)
        self._logger = logger

        # Okay fuck this shit I can't be arsed enough to refactor everything below
        # Bummer for you I guess

        # ======== FORMATTERS ========
        formatter_full = logging.Formatter(
            fmt="[%(asctime)s %(levelname)s] %(message)s"
        )
        formatter_full_color = ColoredFormatter(
            fmt="[%(asctime)s %(levelname)s] %(message)s"
        )
        formatter_shorttime_color = ColoredFormatter(
            fmt="[%(asctime)s %(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )

        # ======== CONSOLE HANDLER ===================
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter_shorttime_color)

        # logger_discord.addHandler(ch) #duplicates messages, I think
        logger.addHandler(ch)

        # ======== FILE HANDLERS ===================
        if not filename:
            filename = self.DEFAULT_LOG_FILE

        filename_plaintext = self._add_suffix_to_filename(
            filename, self.DEFAULT_PLAINTEXT_SUFFIX
        )
        filename_discord = self._add_suffix_to_filename(
            filename, self.DEFAULT_DISCORD_SUFFIX
        )

        self._setup_log_directory()

        # MAIN LOG FILE
        fh = self._create_default_filehandler(filename, level, formatter_full_color)
        fh_discord = self._create_default_filehandler(
            filename, logging.WARNING, formatter_full_color
        )

        # DIFF LOG FILES
        fh_plain = self._create_default_filehandler(
            filename_plaintext, level, formatter_full
        )
        fh_plain_discord = self._create_default_filehandler(
            filename_plaintext, logging.WARNING, formatter_full
        )
        fh_discordfile = self._create_default_filehandler(
            filename_discord, level, formatter_full_color
        )
        self.discord_handler = fh_discordfile

        logger.addHandler(fh)
        logger.addHandler(fh_plain)
        logger_discord.addHandler(fh_discord)
        logger_discord.addHandler(fh_plain_discord)
        # logger_discord.addHandler(fh_discordfile)

        # add a new line to all log files
        # FUCK YOU WHY IS MAP LAZY
        list(
            map(
                self._write_newline_to_logfile,
                (filename, filename_discord, filename_plaintext),
            )
        )

        # DISCORD
        # self._set_discord_logger_configs(fh_discordfile)

    # ==== Public methods ====
    def get_discord_logging_handler(self) -> logging.Handler | None:
        if not self.discord_handler:
            logging.warning("Discord handler is not yet initialised.")
            return None
        return self.discord_handler

    # ==== Logger setup ====
    def _get_main_logger(self, min_level: int) -> logging.Logger:
        logger = logging.getLogger()
        logger.setLevel(min_level)
        return logger

    def _get_discord_logger(self, min_level: int) -> logging.Logger:
        discord_logger = logging.getLogger("discord")
        discord_logger = logging.getLogger()
        discord_logger.setLevel(min_level)
        return discord_logger

    def _set_discord_logger_configs(self, handler: logging.Handler) -> None:
        """Configures the Discord logger, I have to do this for... reasons??"""
        discord.utils.setup_logging(handler=handler, level=logging.WARNING)

    # ==== Handlers ====
    def _create_default_filehandler(
        self, filename: str, level: int, formatter: logging.Formatter
    ) -> logging.Handler:
        """Creates a default file handler using ConcurrentRotatingFileHandler.
        10 MB, 5 backups.

        Args:
            filename (str): Log file name.
            level (int): Logging level.
            formatter (logging.Formatter): Formatter to use

        Returns:
            Handler.Logger: The Handler instance.
        """
        cfh = ConcurrentRotatingFileHandler(
            self._create_full_log_filepath(filename=filename),
            "a",
            maxBytes=20 * 1024 * 1024,
            backupCount=5,
        )
        cfh.setLevel(level)
        cfh.setFormatter(formatter)

        return cfh

    # ==== Filenames ====

    def _create_full_log_filepath(self, filename: str) -> str:
        """Creates the full file path for a log output file

        Args:
            filename (str): Filename.

        Returns:
            str: File path including path to the log directory.
        """
        return os.path.join(self.LOG_PATH, filename)

    def _add_suffix_to_filename(self, filename: str, suffix: str) -> str:
        """Adds a suffix to a supplied filename (with extension)

        Args:
            filename (str): Filename to be appended to.
            suffix (str): Suffix to append.

        Returns:
            str: Filename with appended suffix.
        """
        replaced = re.sub(r"(\.[A-Za-z0-9]{3,4}$)", suffix + r"\1", filename)
        return replaced

    # ==== File System ====

    def _setup_log_directory(self) -> None:
        """Sets up the directory for log files, i.e. creates the directory if it does not exist."""
        # create dir first
        if not os.path.exists(self.LOG_PATH):
            os.mkdir(self.LOG_PATH)

    def _write_newline_to_logfile(self, filename: str) -> None:
        """Writes a new line to the specified log file. Path to log file must exist.

        Args:
            filename (str): Log file to write to. Filename should be relative to the ./logs/ directory.
        """

        with open(self._create_full_log_filepath(filename), "a", encoding="utf-8") as f:
            f.write(
                "-------------------------------------------------------"
                + "-----------------------------------------------------------------\n"
            )
            f.close()


def format_message_from_level(message: str, level: int) -> str:
    return colorize_string(message, LOG_LEVEL_COLORS.get(level, Colors.PURPLE))


class ColoredFormatter(logging.Formatter):
    DEFAULT_FORMAT = "[%(asctime)s %(levelname)s]: %(message)s"

    def __init__(self, *args, **kwargs):
        if "fmt" in kwargs:
            self.used_format = kwargs["fmt"]
        else:
            self.used_format = self.DEFAULT_FORMAT

        self.kwargs = kwargs
        self.args = args

        super().__init__(*args, **kwargs)

    def format(self, record):
        color_appended_format = format_message_from_level(
            self.used_format, record.levelno
        )
        self.kwargs["fmt"] = color_appended_format
        colored_formatter = logging.Formatter(*self.args, **self.kwargs)

        return colored_formatter.format(record)


# For manual testing
def main():
    # setup
    # note that filename is always this random testing file
    LogConfig().setup(is_debug=True, filename="_TEST.log")

    # test formatting
    logging.debug("debug")
    logging.info("info")
    logging.warning("warning")
    logging.error("error")
    logging.critical("critical")
