# business logic for base RP (metadata) functions that uses repositories
"""
Required functions:
* ~~[X] initial update - load all RPs and events from DB, add unscheduled events~~
* [V] get all RPs from server id
* [V] trigger RP tick event - updates RP in DB and then schedules next event
    * called by either rp_cog or scheduler
* [ ] get next tick event for RP
"""

import logging
import math
from datetime import datetime
from typing import Callable

from discord.ext import commands

from cidderbot.models.models import Rp, TickEvent
from cidderbot.repositories.event_repository import EventRepository
from cidderbot.repositories.rp_repository import RpRepository
from cidderbot.services.database import SessionLocal


class RpMetaService:

    def __init__(self, bot: commands.Bot):
        self._session = SessionLocal()
        self.events = EventRepository(self._session)
        self.rps = RpRepository(self._session)

        self._bot = bot

        self._new_event_callback: Callable = None
        self._event_queue = []

    # callback to Scheduler
    def establish_callback(self, on_event_callback: Callable, event_queue):
        self._new_event_callback = on_event_callback
        self._event_queue = event_queue

    async def initiate_rp_tickover(self, tick_event: TickEvent):
        rp_id = tick_event.rp_id
        curr_exec_time = tick_event.execution_time

        try:
            rp = self.rps.get_rp_by_id(rp_id)
            if not rp:
                logging.warning("rpmeta: rp %s not found in DB", rp_id)
                return None

            time_now = datetime.now()
            # account for all ticks passed since last update, in case tickevent was too long ago
            # TODO needs better & clearer error management
            num_passed_ticks = math.ceil(
                (time_now - curr_exec_time) / rp.tickinterval_real
            )
            print(num_passed_ticks)

            rp.curr_time_rp += num_passed_ticks * rp.tickinterval_rp
            self._session.commit()
            next_exec_time = curr_exec_time + num_passed_ticks * rp.tickinterval_real

            print(rp.curr_time_rp, next_exec_time, curr_exec_time)

            # send update message to rp.update_channel_id
            # TODO move somewhere else pls, having it here is BAD
            channel = self._bot.get_channel(rp.update_channel_id)

            if not channel:
                logging.warning(
                    "%s: channel with id %s cannot be retrieved. Update cancelled.",
                    rp,
                    rp.channel_id,
                )
                return False

            # send message
            message = f"Time in {rp.name} is now {rp.curr_time_rp}."
            await channel.send(message)

            # new event with pending status
            new_tickevent = TickEvent(
                execution_time=next_exec_time,
                status="pending",
                rp_id=rp_id,
            )

            self._new_event_callback(new_tickevent)
        except Exception as e:
            logging.error("rpmeta: tickover failed", e)
            return None

    def get_rps_for_server(self, server_id: int) -> list[Rp]:
        return self.rps.get_rps_of_server(server_id)

    def get_next_rp_tickevent(self, rp_id: int):
        # doesn't check event type atm
        return [event for event in self._event_queue if event.rp_id == rp_id][0]
