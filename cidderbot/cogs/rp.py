import logging
from datetime import datetime, timedelta
from typing import List

from discord.ext import commands

from cidderbot.models.guilds import CidderGuild
from cidderbot.utils.time_formatters import (
    TimeUnit,
    convert_time_unit_string,
    format_timedelta,
)


class Rp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def test(self, ctx, member: commands.MemberConverter, *, reason=None):
    #     # await ctx.guild.ban(member, reason=reason)
    #     # await ctx.send(f'{member} has been banned.')
    #     pass


def setup(bot):
    bot.add_cog(Rp(bot))


class RpHandler:
    def __init__(
        self,
        name: str,
        guilds: List[CidderGuild],
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

    def __repr__(self) -> str:
        return f"<RP: {self.name}>"

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
            + f"to {self.current_rp_time_string()}. "
            + f"Next update is in {self.get_time_to_next_increment_string()}."
        )

    def increment(self, initial: datetime, unit: TimeUnit, value: int) -> datetime:
        if unit == TimeUnit.YEAR:
            return initial.replace(year=value * initial.year)
        elif unit == TimeUnit.MONTH:
            return initial.replace(year=value * initial.year)

        return initial + unit.value

    def current_rp_time_string(self) -> str:
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
