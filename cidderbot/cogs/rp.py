import asyncio
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import List

import discord
from discord.ext import commands

from cidderbot.models.models import Rp
from cidderbot.services.rp_meta_service import RpMetaService
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

    def __init__(self, bot: commands.Bot, rp_meta_service: RpMetaService):
        self.bot = bot
        self.rp_meta_service = rp_meta_service

    # ====================== Commands START =======================================

    @commands.command()
    async def date(self, ctx: commands.Context):
        """Shows the current date of the RP.

        Example:
        The current date in <TheRP> is Jan 1970.
        Next year is in 1 day and 2 hours.
        """
        rps: list[Rp] = self._get_rps(ctx)
        rp_messages = []

        for rp in rps:
            curr_time_str = rp.format_current_rp_time()
            # next_rp_time = format_timedelta(rp.get_time_to_next_rp_unit(), 3)

            # TODO "next 2 years" not supported
            message_list = [
                f"Current date in Sagrea is {curr_time_str}.",
                # f"-# *Next {rp.rp_datetime_unit.name.lower()} is in {next_rp_time}*",
            ]

            message = "\n".join(message_list)
            rp_messages.append(message)

        await ctx.send("\n".join(rp_messages))

    @commands.command()
    async def info(self, ctx: commands.Context):
        """Shows a printout of the current info of the RP."""
        rps: list[Rp] = self._get_rps(ctx)
        rp_messages = []

        for rp in rps:
            message_list = [
                f"### RP info for {rp.name}:",
                f"It is currently {rp.curr_time_rp}.",
                f"Updates every {format_timedelta(rp.tickinterval_real)}.",
                "",
            ]

            use_discord_timestamp = False

            # Now add "It will be X rp datetime in Y duration"
            # If both incr_unit and unit are the same, only include one

            # add unit first cuz assumed to be smaller.
            # currently discord timestamp is disabled based on user feedback

            # TODO: next RP time not working, should call rp_meta_service
            use = False
            # next_unit_utc_timestamp = int(
            #     convert_datetime_to_utc_timestamp(rp.next_unit_datetime)
            # )
            # next_rp_time = format_timedelta(rp.get_time_to_next_rp_unit(), 1)
            # message_list.append(
            #     f"It will be {rp.format_next_rp_time()} in {next_rp_time}, at <t:{next_unit_utc_timestamp}:f>."
            # )
            # if rp.rp_datetime_unit != rp.rp_datetime_incr_unit:
            #     next_incr_utc_timestamp = int(
            #         convert_datetime_to_utc_timestamp(rp.next_incr_datetime)
            #     )
            #     next_rp_incr = format_timedelta(rp.get_time_to_next_incr(), 1)
            #     message_list.append(
            #         f"It will be {rp.format_next_rp_incr_time()} in {next_rp_incr}, at <t:{next_incr_utc_timestamp}:f>."
            #     )

            message = "\n".join(message_list)
            rp_messages.append(message)

        await ctx.send("\n".join(rp_messages))

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

    def _get_rp(self, ctx: commands.Context) -> Rp:
        # get first only
        return self._get_rps(ctx)[0]

    def _get_rps(self, ctx: commands.Context) -> list[Rp]:
        # get all
        assert ctx.guild, "I don't know what happens if this is None"

        server_id = ctx.guild.id
        return self.rp_meta_service.get_rps_for_server(server_id)


# required global function for bot.load_extension()
def setup(bot):
    bot.add_cog(Rp(bot))
