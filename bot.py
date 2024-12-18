import asyncio
import os
import pkgutil

import discord
from discord.ext import commands
from dotenv import load_dotenv

from events import events

# should move to a constants file
TOKEN_STRING = 'DISCORD_TOKEN'
COMMAND_PREFIX = '$'
# INTENTS_INTEGER = 182272

class BotMain():
    """Class used to handle bot startup"""

    def __init__(self) -> None:
        """Initiallises the bot."""

        print("Bot initialising...")

        self.bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=self._setupIntents())

        self._loadTokens()
        self._loadCogs()

        events.BotEvents(self.bot)

        self.bot.run(self.TOKEN)

    def _setupIntents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.message_content = True

        return intents

    def _loadTokens(self) -> None:
        """Loads tokens into the object."""

        load_dotenv()
        self.TOKEN = os.getenv(TOKEN_STRING)

    def _loadCogs(self) -> None:
        """Loads Cogs (in `./cogs/*`) into the bot."""

        for _, name, _ in pkgutil.iter_modules(['cogs']):
            self.bot.load_extension(f'cogs.{name}')


def main():
    BotMain()

if __name__ == "__main__":
    main()