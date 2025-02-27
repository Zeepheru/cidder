import asyncio
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

        # load scheduling events for all RPs
        for rp in self.cidder.rps:
            self.update_rp_regular_task(rp)

    def _get_rp(self, ctx) -> "RpHandler":
        # very advanced code :+1:
        return self.cidder.get_rps_for_guild(ctx.guild)[0]

    @commands.command()
    async def date(self, ctx):
        rp: RpHandler = self._get_rp(ctx)

        curr_time_str = rp.format_current_rp_time_string()
        next_update_time_str = rp.format_time_to_next_increment()

        message = (
            f"Current time in Sagrea is {curr_time_str}.\n"
            + f"-# *Next update is in {next_update_time_str}*"
        )
        await ctx.send(message)

    @commands.command()
    async def info(self, ctx):
        rp: RpHandler = self._get_rp(ctx)

        value = rp.rp_datetime_increment_amount

        message = (
            f"### RP info for {rp.name}:\n"
            + f"Current date: {rp.format_current_rp_time_string()}\n"
            + f"Update frequency: {format_timedelta(rp.incr_interval)}\n"
            + f"Next update: {value} {rp.rp_datetime_unit.name.lower()}{"" if value == 1 else "s"} "
            + f"to {rp.format_next_rp_time()}, in {rp.format_time_to_next_increment()}"
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

    def update_rp(self, rp: "RpHandler"):
        """Updates the RP (increments), and sends a message to the update channel id specified in the rp instance.

        Args:
            rp (RpHandler): rp instance to be updated.
        """

        if not rp.channel_id:
            logging.warning("%s: invalid channel id. Update cancelled.", rp)
            return
        channel = self.bot.get_channel(rp.channel_id)

        if not channel:
            logging.warning(
                "%s: channel with id %s cannot be retrieved. Update cancelled.",
                rp,
                rp.channel_id,
            )
            return

        # update
        rp.update()

        # send message
        message = f"Time in {rp.name} is now {rp.format_current_rp_time_string()}."
        channel.send(message)

    async def update_rp_regular_task(self, rp: "RpHandler"):
        await self.bot.wait_until_ready()

        # schedule next update event
        logging.info(
            "%s: Next Update event is scheduled in: %s",
            rp,
            rp.format_time_to_next_increment(),
        )
        time_till_next_update = rp.get_time_to_next_increment()
        asyncio.sleep(time_till_next_update.seconds())
        self.update_rp(rp)

        while not self.bot.is_closed():
            asyncio.sleep(time_till_next_update.seconds())
            self.update_rp(rp)


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
        channel_id: int = 0,
    ) -> None:
        self.guilds = guilds
        self.name = name
        self.rp_datetime_unit = rp_datetime_unit
        self.rp_datetime = rp_datetime
        self.rp_datetime_increment_amount = rp_datetime_increment_amount
        self.prev_incr_datetime = prev_datetime
        self.next_incr_datetime = prev_datetime + increment_interval
        self.incr_interval = increment_interval
        self.channel_id = channel_id

        self._update_date_to_current()

        logging.info(
            "%s loaded. Current time: %s", self, self.format_current_rp_time_string()
        )

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

        self.rp_datetime = self.increment(
            self.rp_datetime,
            self.rp_datetime_unit,
            update_count * self.rp_datetime_increment_amount,
        )

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
            + f"to {self.format_current_rp_time_string()}. "
            + f"Next update is in {self.format_time_to_next_increment()}."
        )

    def increment(self, initial: datetime, unit: TimeUnit, value: int) -> datetime:
        if unit == TimeUnit.YEAR:
            temp = value + initial.year
            new = initial.replace(year=value + initial.year)
            return new
        elif unit == TimeUnit.MONTH:
            return initial.replace(month=value + initial.month)

        return initial + unit.value

    def get_time_to_next_increment(self) -> timedelta:
        return self.next_incr_datetime - datetime.now()

    def format_current_rp_time_string(self) -> str:
        """Gets the current in-RP time as a formatted string, based on the unit used for the RP.

        Returns:
            str: Formatted time as a string.
        """
        return convert_time_unit_string(self.rp_datetime, self.rp_datetime_unit)

    def format_next_rp_time(self) -> str:
        """Gets the in-RP time as of the next updated as a formatted string, based on the unit used for the RP.

        Returns:
            str: Formatted next update time as a string.
        """
        return convert_time_unit_string(
            self.increment(
                self.rp_datetime,
                self.rp_datetime_unit,
                self.rp_datetime_increment_amount,
            ),
            self.rp_datetime_unit,
        )

    def format_time_to_next_increment(self) -> str:
        """Gets the real-life duration to the next increment as a formatted string.

        Returns:
            str: Formatted duration to next increment.
        """

        return format_timedelta(self.get_time_to_next_increment())
