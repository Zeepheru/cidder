import logging
import os
import pkgutil

import discord
from discord.ext import commands
from dotenv import load_dotenv

from events import events
from utils import log_config

# should move to a constants file
TOKEN_STRING = 'DISCORD_TOKEN'
DEBUG_MODE_STRING = 'DEBUG_MODE'
COMMAND_PREFIX = '$'
# INTENTS_INTEGER = 182272

class BotMain():
    """Class used to handle bot startup."""

    _logger: logging.Logger

    def __init__(self) -> None:
        """Initiallises the bot.
        """

        print("Bot initialising...")

        # load logger
        is_debug = os.getenv(DEBUG_MODE_STRING) == "1"
        log_config.LogConfig().setup(is_debug=is_debug)
        self._logger = logging.getLogger()
        self._logger.info("Logging setup complete.")
        self._logger.debug("Program running in %s.", os.getcwd())

        self.bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=self._setup_intents())

        # load tokens and cogs
        self._load_tokens()
        self._logger.info("Token loading complete.")
        self._load_cogs()
        self._logger.info("Cog loading complete.")

        events.BotEvents(self.bot)

        self.bot.run(self._token)

    def _setup_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.message_content = True

        return intents

    def _load_tokens(self) -> None:
        """Loads tokens into the object."""

        load_dotenv()
        self._token = os.getenv(TOKEN_STRING)

    def _load_cogs(self) -> None:
        """Loads Cogs (in `./cogs/*`) into the bot."""

        for _, name, _ in pkgutil.iter_modules(['cogs']):
            self.bot.load_extension(f'cogs.{name}')

def main():
    BotMain()

if __name__ == "__main__":
    main()
