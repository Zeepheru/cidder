import logging

import discord
from discord.ext import commands


class BotEvents:
    """Class to handle bot events."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._register_events()
        self._logger = logging.getLogger()

    def _register_events(self) -> None:
        """Registers all events."""

        @self.bot.event
        async def on_ready() -> None:
            if self.bot.user:
                self._logger.info(
                    "Bot is ready. Logged in as %s | ID:%s",
                    self.bot.user,
                    self.bot.user.id,
                )
            else:
                self._logger.warning("Bot is ready but not logged in.")

        @self.bot.event
        async def on_message(message: discord.Message) -> None:
            # Ref: https://github.com/GreatTaku/Discord-Bot-Examples/blob/master/async/on_message.py
            content = message.content
            user = message.author
            channel = message.channel

            # ignore if message is from itself
            if user == self.bot.user:
                return
            self._logger.info("[%s in %s]: %s", user, channel, content)
