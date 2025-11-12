import asyncio
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import List

import discord
from discord.ext import commands

from cidderbot.utils.time_formatters import (
    TimeUnit,
    convert_datetime_to_utc_timestamp,
    convert_time_unit_string,
    format_timedelta,
    get_time_unit_mapping,
)


# I can't type annotate cidder because of circular imports. Must mean this whole thing is incredibly jank.
# And there probably is a "correct" way I can't be arsed to figure out.
class Rp(commands.Cog):

    def __init__(self, bot: commands.Bot, cidder: "cidderbot.cidder.Cidder"):
        self.bot = bot
        self.cidder = cidder

        for rp in self.cidder.rps:
            self.bot.loop.create_task(self.update_rp_regular_task(rp))

    # ====================== Commands START =======================================

    @commands.command()
    async def date(self, ctx: commands.Context):
        """Shows the current date of the RP.

        Example:
        The current date in <TheRP> is Jan 1970.
        Next year is in 1 day and 2 hours.
        """
        rp: RpHandler = self._get_rp(ctx)

        curr_time_str = rp.format_current_rp_time()
        next_rp_time = format_timedelta(rp.get_time_to_next_rp_unit(), 3)

        # TODO this currently won't display any increment values - i.e. only shows Next year instead of Next 2 years.
        messsage_list = [
            f"Current date in Sagrea is {curr_time_str}.",
            f"-# *Next {rp.rp_datetime_unit.name.lower()} is in {next_rp_time}*",
        ]

        message = "\n".join(messsage_list)

        await ctx.send(message)

    @commands.command()
    async def info(self, ctx: commands.Context):
        """Shows a printout of the current info of the RP."""
        rp: RpHandler = self._get_rp(ctx)

        message_list = [
            f"### RP info for {rp.name}:",
            f"It is currently {rp.format_current_rp_time()}.",
            f"Updates every {format_timedelta(rp.incr_interval)}.",
            "",
        ]

        use_discord_timestamp = False

        # Now add "It will be X rp datetime in Y duration"
        # If both incr_unit and unit are the same, only include one

        # add unit first cuz assumed to be smaller.
        # currently discord timestamp is disabled based on user feedback
        use = False
        next_unit_utc_timestamp = int(
            convert_datetime_to_utc_timestamp(rp.next_unit_datetime)
        )
        next_rp_time = format_timedelta(rp.get_time_to_next_rp_unit(), 1)
        message_list.append(
            f"It will be {rp.format_next_rp_time()} in {next_rp_time}, at <t:{next_unit_utc_timestamp}:f>."
        )
        if rp.rp_datetime_unit != rp.rp_datetime_incr_unit:
            next_incr_utc_timestamp = int(
                convert_datetime_to_utc_timestamp(rp.next_incr_datetime)
            )
            next_rp_incr = format_timedelta(rp.get_time_to_next_incr(), 1)
            message_list.append(
                f"It will be {rp.format_next_rp_incr_time()} in {next_rp_incr}, at <t:{next_incr_utc_timestamp}:f>."
            )

        message = "\n".join(message_list)

        await ctx.send(message)

    # @commands.command()
    # async def test(self, ctx: commands.Context):
    #     rp: RpHandler = self._get_rp(ctx=ctx)

    #     # message = "%s\n%s\n%s\n%s"
    #     message = "TEST."
    #     print(rp.num_units_in_incr)
    #     print(rp.get_current_rp_unit_time())
    #     print(rp.format_time_to_next_incr())
    #     print(rp.get_time_to_next_rp_unit())

    #     await ctx.send(message)

    # ====================== Commands END =======================================

    async def initialize(self) -> None:
        """Asynchronous initializations required for Rp."""
        # load scheduling events for all RPs
        for rp in self.cidder.rps:
            await self.update_rp_regular_task(rp)

    def _get_rp(self, ctx: commands.Context) -> "RpHandler":
        # very advanced code :+1:
        return self.cidder.get_rps_for_guild(ctx.guild)[0]

    def _get_custom_messages(self, rp: "RpHandler") -> str:
        custom_messages = []

        rp_dt = rp.get_current_rp_unit_time()

        # april fools - only if the increment unit is DAY
        if (
            rp.rp_datetime_incr_unit == TimeUnit.DAY
            and rp_dt.day == 1
            and rp_dt.month == 4
        ):
            custom_messages.append("Happy April Fools!")

        return "\n".join(custom_messages)

    async def update_rp(self, rp: "RpHandler") -> bool:
        """Updates the RP by incrementing the date,
        and sends a message to the update channel id specified in the rp instance.

        Args:
            rp (RpHandler): rp instance to be updated.

        Returns:
            bool: Success: True; Failure: False
        """

        if not rp.channel_id:
            # TODO: this should continue to update, just without sending an update message
            logging.warning("%s: invalid channel id. Update cancelled.", rp)
            return False
        channel = self.bot.get_channel(rp.channel_id)

        if not channel:
            logging.warning(
                "%s: channel with id %s cannot be retrieved. Update cancelled.",
                rp,
                rp.channel_id,
            )
            return False

        # update
        rp.update()

        # send message
        message = f"Time in {rp.name} is now {rp.format_current_rp_time()}."

        # append extra messages depending on the RP
        message += self._get_custom_messages(rp=rp)

        await channel.send(message)

        return True

    async def update_rp_regular_task(self, rp: "RpHandler"):
        await self.bot.wait_until_ready()

        # schedule next update event
        logging.info(
            "%s: Next Update event is scheduled in: %s",
            rp,
            rp.format_time_to_next_incr(),
        )
        time_till_next_update = rp.get_time_to_next_incr()
        await asyncio.sleep(time_till_next_update.total_seconds())
        await self.update_rp(rp)  # note - continues even on failure

        while not self.bot.is_closed():
            await asyncio.sleep(rp.incr_interval.total_seconds())
            await self.update_rp(rp)


# required global function for bot.load_extension()
def setup(bot):
    bot.add_cog(Rp(bot))


class RpHandler:
    """Class that encapsulates an RP instance."""

    def __init__(
        self,
        name: str,
        guilds: List[discord.Guild],
        rp_datetime_unit: TimeUnit,
        rp_datetime_incr_unit: TimeUnit,
        rp_datetime: datetime,
        rp_datetime_incr_amount: int,
        last_datetime: datetime,
        incr_interval: timedelta,
        channel_id: int = 0,
    ) -> None:
        """Creates a new RpHandler instance to wrap an RP.

        #TODO: in future this will probably only handle date information.

        Args:
            name (str): Name of this RP.
            guilds (List[discord.Guild]): List of Guilds (servers). Currently using `discord.Guild`,
                but expected to change in future to own class.
            rp_datetime_unit (TimeUnit): Smallest unit to be tracked and displayed in this RP.
            rp_datetime (datetime): Current RP date/time.
            rp_datetime_incr_amount (int): Amount to be used for regular RP date/time increments.
            rp_datetime_incr_unit (TimeUnit): Unit to be used for regular RP date/time increments.
            last_datetime (datetime): Last real-life date/time that the RP was incremented on.
            incr_interval (timedelta): Real-life time interval between RP date/time increments.
            channel_id (int, optional): Channel id to send RP date/time increment messages to.
                Defaults to 0, which disables update messages.
                #TODO: this should be a list of channels.
        """
        self.guilds = guilds
        self.name = name
        self.rp_datetime_unit = rp_datetime_unit
        self.rp_datetime_incr_unit = rp_datetime_incr_unit
        self.rp_datetime = rp_datetime
        self.rp_datetime_incr_amount = rp_datetime_incr_amount
        self.prev_incr_datetime = last_datetime
        self.next_incr_datetime = last_datetime + incr_interval
        self.incr_interval = incr_interval
        self.channel_id = channel_id

        # number of units in an increment interval
        self.num_units_in_incr = rp_datetime_incr_amount * get_time_unit_mapping(
            self.rp_datetime_incr_unit, rp_datetime_unit
        )

        # loaded parameters may be out of date, so update them to current.
        self._update_date_to_current()

        logging.info("%s loaded. Current time: %s", self, self.format_current_rp_time())

    def __repr__(self) -> str:
        return f"<RP: {self.name}>"

    def _update_date_to_current(self) -> None:
        """Updates the date of the rp to the correct current date based on how many update cycles may have passed
        since the loaded start time.

        Also updates prev and next incr_time

        Accounts for incorrect start times.
        """
        duration_since_start = datetime.now(timezone.utc) - self.prev_incr_datetime
        if duration_since_start < self.incr_interval:
            return

        update_count = math.floor(duration_since_start / self.incr_interval)

        self.rp_datetime = self.add_to_datetime(
            self.rp_datetime,
            self.rp_datetime_incr_unit,
            update_count * self.rp_datetime_incr_amount,
        )

        # update incr times
        self.prev_incr_datetime += update_count * self.incr_interval
        self.next_incr_datetime = self.prev_incr_datetime + self.incr_interval

    def update(self) -> None:
        """Updates the in-universe and real dates of this RP instance."""
        prev_rp_dt = self.rp_datetime
        self.rp_datetime = self.add_to_datetime(
            self.rp_datetime,
            self.rp_datetime_incr_unit,
            self.rp_datetime_incr_amount,
        )

        self.prev_incr_datetime = self.next_incr_datetime
        self.next_incr_datetime += self.incr_interval

        logging.info(
            "%s has been updated from %s to %s. Next update is in %s.",
            self,
            convert_time_unit_string(prev_rp_dt, self.rp_datetime_incr_unit),
            self.format_current_rp_time(),
            self.format_time_to_next_incr(),
        )

    def add_to_datetime(
        self, initial: datetime, unit: TimeUnit, value: int
    ) -> datetime:
        """Add a given datetime by an amount value * unit.

        Args:
            initial (datetime): Initial datetime to add to.
            unit (TimeUnit): Unit of time.
            value (int): Amount of unit to add by. Accepts positive integer values only.

        Returns:
            datetime: Added datetime.
        """
        # negative check
        if value < 0:
            logging.warning("Tried to add a negative value %s. Not allowed.", value)
            return initial

        # Month and year need this kinda code to add, otherwise not necessary.
        # Saying this is going to bite me in the ass because I think I missed out leap years' days.
        if unit == TimeUnit.YEAR:
            # temp = value + initial.year
            new = initial.replace(year=value + initial.year)
            return new
        elif unit == TimeUnit.MONTH:
            years, months = divmod(value, 12)
            return initial.replace(
                year=years + initial.year,
                month=months + initial.month,
            )

        add_delta = timedelta(seconds=unit.value * value)

        return initial + add_delta

    # ================================ Time GETTERS =============================================

    @property
    def next_unit_datetime(self) -> datetime:
        now = datetime.now(timezone.utc)
        time_since_incr = now - self.prev_incr_datetime
        fraction_elapsed = time_since_incr / self.incr_interval

        num_units_next_unit_time = math.ceil(fraction_elapsed * self.num_units_in_incr)

        # These are some variable names.
        next_unit_time_irl_time_from_last_incr = (
            num_units_next_unit_time / self.num_units_in_incr * self.incr_interval
        )

        return next_unit_time_irl_time_from_last_incr + self.prev_incr_datetime

    def get_time_to_next_incr(self) -> timedelta:
        """Gets the real-life time until the next increment is scheduled.

        Returns:
            timedelta: Time until the next increment.
        """
        now = datetime.now(timezone.utc)
        difference = self.next_incr_datetime - now
        return difference

    def get_time_to_next_rp_unit(self) -> timedelta:
        """Gets the time until the next RP time based on the specified precision unit.

        Returns:
            timedelta: Time until the next RP time.
        """
        now = datetime.now(timezone.utc)
        time_to_next_unit_time = self.next_unit_datetime - now

        return time_to_next_unit_time

    def get_current_rp_unit_time(self) -> datetime:
        """Gets the current RP time, precision is the unit specified in the RP parameters.

        Returns:
            datetime: Current RP unit time.
        """
        now = datetime.now(timezone.utc)
        time_since_incr = now - self.prev_incr_datetime
        fraction_elapsed = time_since_incr / self.incr_interval

        num_units_elapsed = math.floor(fraction_elapsed * self.num_units_in_incr)

        new_dt = self.add_to_datetime(
            initial=self.rp_datetime,
            unit=self.rp_datetime_unit,
            value=num_units_elapsed,
        )

        return new_dt

    def get_next_rp_unit_time(self) -> datetime:
        """Gets the next RP time, precision is the unit specified in the RP parameters.

        Returns:
            datetime: Next RP unit time.
        """
        now = datetime.now(timezone.utc)
        time_since_incr = now - self.prev_incr_datetime
        fraction_elapsed = time_since_incr / self.incr_interval

        num_units_elapsed_next = math.ceil(fraction_elapsed * self.num_units_in_incr)

        new_dt = self.add_to_datetime(
            initial=self.rp_datetime,
            unit=self.rp_datetime_unit,
            value=num_units_elapsed_next,
        )

        return new_dt

    # ================================ FORMATTED RETURNS =================================

    def format_current_rp_time(self) -> str:
        """Formats the current in-RP time, based on the unit used for the RP.

        Returns:
            str: Formatted time as a string.
        """
        return convert_time_unit_string(
            self.get_current_rp_unit_time(), self.rp_datetime_unit
        )

    def format_current_rp_incr_time(self) -> str:
        """Formats the current in-RP time, based on the increment unit used for the RP.

        Returns:
            str: Formatted time as a string.
        """
        return convert_time_unit_string(
            self.get_current_rp_unit_time(), self.rp_datetime_incr_unit
        )

    def format_next_rp_time(self) -> str:
        """Formats the in-RP time as of the next increment, based on the unit used for the RP.

        Returns:
            str: Formatted next unit time as a string.
        """
        return convert_time_unit_string(
            self.get_next_rp_unit_time(), self.rp_datetime_unit
        )

    def format_next_rp_incr_time(self) -> str:
        """Formats the in-RP time as of the next increment, based on the increment unit used for the RP.

        Returns:
            str: Formatted next increment time as a string.
        """
        return convert_time_unit_string(
            dt=self.add_to_datetime(
                initial=self.rp_datetime,
                unit=self.rp_datetime_incr_unit,
                value=self.rp_datetime_incr_amount,
            ),
            unit=self.rp_datetime_incr_unit,
        )

    def format_time_to_next_incr(self) -> str:
        """Formats the real-life duration to the next increment

        Returns:
            str: Formatted duration to next increment.
        """

        return format_timedelta(self.get_time_to_next_incr())
