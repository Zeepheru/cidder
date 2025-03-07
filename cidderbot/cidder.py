import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List

import discord

from cidderbot.cogs.rp import RpHandler
from cidderbot.utils.time_formatters import TimeUnit


class Cidder:
    """Primary access point for all of Cidder's features. Initialized through the on_ready() event,
    after the bot is ready.
    """

    def __init__(self) -> None:
        """Creates an empty, uninitialized instance of Cidder."""
        self._initialized = False

        # fields
        self.guilds = []
        self.channels = []
        self.users = []
        self.rps = []

    def initialize(
        self,
        guilds: List[discord.Guild],
        channels: List[discord.ChannelType],
        users: List[discord.User],
    ) -> None:
        # Initialize Cidder **after** the bot is ready
        self.guilds = guilds
        self.channels = channels
        self.users = users
        self.rps = []

        # initialize RP Handler
        # load env vars (temp solution trust)
        name = os.getenv("RP_NAME")
        rp_datetime_unit = os.getenv("RP_DT_UNIT")
        rp_datetime_incr_unit = os.getenv("RP_DT_INCR_UNIT")
        rp_datetime_string = os.getenv("RP_DT_ISOSTRING")
        rp_datetime_increment_amount = int(os.getenv("RP_DT_INCR_AMT"))
        prev_datetime_string = os.getenv("PREV_INCR_DT_ISOSTRING")
        increment_interval_secs = int(os.getenv("INCR_INTERVAL_SECONDS"))

        channel_id = int(os.getenv("CHANNEL_ID"))

        # convert datetimes first
        rp_datetime = datetime.fromisoformat(rp_datetime_string).replace(
            tzinfo=timezone.utc
        )
        rp_last_datetime = datetime.fromisoformat(prev_datetime_string).replace(
            tzinfo=timezone.utc
        )

        rp = RpHandler(
            name=name,
            guilds=self.guilds,
            rp_datetime_unit=TimeUnit[rp_datetime_unit],
            rp_datetime_incr_unit=TimeUnit[rp_datetime_incr_unit],
            rp_datetime=rp_datetime,
            rp_datetime_incr_amount=rp_datetime_increment_amount,
            last_datetime=rp_last_datetime,
            incr_interval=timedelta(seconds=increment_interval_secs),
            channel_id=channel_id,
        )

        self.rps.append(rp)

        self._initialized = True
        logging.info("Main Cidder handler initialized.")

    def _intialized_check(self) -> bool:
        if not self._initialized:
            logging.error("This instance of Cidder has not been initialized!")
            return False
        return True

    def get_rps_for_guild(self, guild: discord.Guild) -> List[RpHandler]:
        """Returns a list of RPs associated with a particular guild.

        Args:
            guild (discord.Guild): Guild object whose RPs are desired.

        Returns:
            List[RpHandler]: List[RpHandler]: List of RP handlers.
        """
        if not self._intialized_check():
            return []

        return [rp for rp in self.rps if guild in rp.guilds]
