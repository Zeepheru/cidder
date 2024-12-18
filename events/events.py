import discord
from discord.ext import commands


class BotEvents:
    """Class to handle bot events."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._registerEvents()

    def _registerEvents(self) -> None:
        """Registers all events."""

        @self.bot.event
        async def on_ready() -> None:
            print(f'Bot is ready. Logged in as {self.bot.user} | ID: {self.bot.user.id}')

        @self.bot.event
        async def on_message(message: discord.Message) -> None:
            # Ref: https://github.com/GreatTaku/Discord-Bot-Examples/blob/master/async/on_message.py
            content = message.content
            user = message.author
            channel = message.channel

            # ignore if message is from itself
            if user == self.bot.user:
                return
            
            print(f"[{user} in {channel}]: {content}")