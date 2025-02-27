import logging
import math
from datetime import datetime, timedelta
from typing import List

import discord
from discord.ext import commands

from cidderbot.utils.time_formatters import (
    TimeUnit,
    convert_time_unit_string,
    format_timedelta,
)


# I can't type annotate cidder because of circular imports. Must mean this whole thing is incredibly jank.
# And there probably is a "correct" way I can't be arsed to figure out.
class Rp(commands.Cog):
    def __init__(self, bot: commands.Bot, cidder):
        self.bot = bot
        self.cidder = cidder

    @commands.command()
    async def date(self, ctx):
        rp: RpHandler = self.cidder.get_rps_for_guild(ctx.guild)[
            0
        ]  # very advanced code :+1:

        curr_time_str = rp.get_current_rp_time_string()
        next_update_time_str = rp.get_time_to_next_increment_string()

        message = (
            f"Current time in Sagrea is {curr_time_str}.\n"
            + f"-# *Next update is in {next_update_time_str}*"
        )
        await ctx.send(message)

    # example
    # @commands.command()
    # async def test(self, ctx, member: commands.MemberConverter, *, reason=None):
    #     # await ctx.guild.ban(member, reason=reason)
    #     # await ctx.send(f'{member} has been banned.')
    #     pass

    # @commands.command()
    # async def hello(self, ctx, *, member: discord.Member = None):
    #     """Says hello"""
    #     member = member or ctx.author
    #     await ctx.send(f"Hello {member.name}~")


# required global function for bot.load_extension()
def setup(bot):
    bot.add_cog(Rp(bot))


class RpHandler:
    def __init__(
        self,
        name: str,
        guilds: List[discord.Guild],
        rp_datetime_unit: TimeUnit,
        rp_datetime: datetime,
        rp_datetime_increment_amount: int,
        prev_datetime: datetime,
        increment_interval: timedelta,
    ) -> None:
        self.guilds = guilds
        self.name = name
        self.rp_datetime_unit = rp_datetime_unit
        self.rp_datetime = rp_datetime
        self.rp_datetime_increment_amount = rp_datetime_increment_amount
        self.prev_incr_datetime = prev_datetime
        self.next_incr_datetime = prev_datetime + increment_interval
        self.incr_interval = increment_interval

        self._update_date_to_current()

    def __repr__(self) -> str:
        return f"<RP: {self.name}>"

    def _update_date_to_current(self) -> None:
        """Updates the date of the rp to the correct current date based on how many update cycles may have passed
        since the loaded start time.

        Accounts for incorrect start times.
        """
        duration_since_start = datetime.now() - self.prev_incr_datetime
        if duration_since_start < self.incr_interval:
            return

        update_count = math.floor(duration_since_start / self.incr_interval)

        self.rp_datetime += update_count * self.incr_interval

    def update(self) -> None:
        """Updates the in-universe and real dates of this RP instance."""
        prev_rp_dt = self.rp_datetime
        self.rp_datetime = self.increment(
            self.rp_datetime,
            self.rp_datetime_unit,
            self.rp_datetime_increment_amount,
        )

        self.prev_incr_datetime = self.next_incr_datetime
        self.next_incr_datetime += self.incr_interval

        logging.info(
            f"{self} has been updated from {convert_time_unit_string(prev_rp_dt, self.rp_datetime_unit)} "
            + f"to {self.get_current_rp_time_string()}. "
            + f"Next update is in {self.get_time_to_next_increment_string()}."
        )

    def increment(self, initial: datetime, unit: TimeUnit, value: int) -> datetime:
        if unit == TimeUnit.YEAR:
            return initial.replace(year=value * initial.year)
        elif unit == TimeUnit.MONTH:
            return initial.replace(year=value * initial.year)

        return initial + unit.value

    def get_current_rp_time_string(self) -> str:
        """Gets the current in-RP time as a formatted string, based on the unit used for the RP.

        Returns:
            str: Formatted time as a string.
        """
        return convert_time_unit_string(self.rp_datetime, self.rp_datetime_unit)

    def get_time_to_next_increment_string(self) -> str:
        """Gets the duration to the next increment and returns it as a formatted string.

        Returns:
            str: Formatted duration to next increment.
        """

        return format_timedelta(self.next_incr_datetime - datetime.now())
