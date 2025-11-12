import logging

import discord
from discord.ext import commands

from cidderbot.cidder import Cidder
from cidderbot.cogs import rp
from cidderbot.services.rp_meta_service import RpMetaService
from cidderbot.services.scheduler import SchedulerService


class BotEvents:
    """Class to handle bot events.

    ### List of events:
    * on_ready() - Initialization event. Also includes proper Cidder startup.
    * on_message() - Event when a message is sent."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._logger = logging.getLogger()

        self._register_events()

    def _register_events(self) -> None:
        """Registers all events."""

        @self.bot.event
        async def on_ready() -> None:
            """When the bot is ready.

            Also handles various service startup procedures.

            Loads cogs.
            """
            if self.bot.user:
                self._logger.info(
                    "Bot is ready. Logged in as %s | ID:%s",
                    self.bot.user,
                    self.bot.user.id,
                )
            else:
                self._logger.warning("Bot is ready but not logged in.")

            # initialization code
            guilds = self.bot.guilds
            channels = self.bot.get_all_channels()
            users = self.bot.users

            # logging.debug(self.bot.cogs)
            # logging.debug(self.bot.command_prefix)

            # Startup scheduler
            rp_meta_service = RpMetaService(self.bot)
            scheduler = SchedulerService(self.bot, rp_meta_service)
            queue = await scheduler.start()
            self._logger.info(
                "Scheduler started with %s pending events loaded.",
                len(queue),
            )

            # load cogs
            rp_cog = rp.Rp(
                self.bot,
                rp_meta_service,
            )
            await self.bot.add_cog(rp_cog)

            self._logger.info("Cog loading complete.")
            self._logger.info("[SUCCESS] CiDder loading complete.")

        @self.bot.event
        async def on_message(message: discord.Message) -> None:
            # Let
            await self.bot.process_commands(message)

            # Ref: https://github.com/GreatTaku/Discord-Bot-Examples/blob/master/async/on_message.py
            content = message.content
            user = message.author
            channel = message.channel
            guild = message.guild

            # ignore if message is from itself
            if user == self.bot.user:
                return
            # log only if necessary
            # self._logger.info("[%s in %s/%s]: %s", user, guild, channel, content)
