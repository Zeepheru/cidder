import asyncio
import heapq
import logging
import time
from datetime import datetime

from discord.ext import commands

from cidderbot.models.models import TickEvent
from cidderbot.repositories.event_repository import EventRepository
from cidderbot.repositories.rp_repository import RpRepository
from cidderbot.services.database import SessionLocal
from cidderbot.services.rp_meta_service import RpMetaService


class SchedulerService:
    def __init__(self, bot: commands.Bot, rp_meta_service: "RpMetaService"):
        self._session = SessionLocal()
        self._rps = RpRepository(self._session)
        self._events = EventRepository(self._session)

        self._bot = bot
        self.rp_meta_service = rp_meta_service
        rp_meta_service.establish_callback(self.schedule_event, self._events)

        # init empty queue
        self._queue = []
        self.running = False

    async def start(self):
        self.running = True
        await self._recover_pending_events()
        self._run_loop()

        print("after")

        return self._queue

    def stop(self):
        self.running = False

    def schedule_event(self, event: TickEvent):
        if not event:
            logging.warning("Attempted to create None event.")
            return

        self._events.add_tick_event(event)
        heapq.heappush(self._queue, EventWrapper(event))

    def schedule_tick_event(
        self,
        rp_id: int,
        exec_time: datetime,
    ):
        # create new event
        event = TickEvent(execution_time=exec_time, status="pending", rp_id=rp_id)
        self.schedule_event(event)

    async def _recover_pending_events(self):
        # Load all unexecuted events from DB
        pending = self._events.get_pending_events()
        print(pending)  # debug

        # print(self._queue)

        for event in pending:
            # if event.execution_time <= datetime.now():
            #     await self._execute_event(event)
            #     self._session.commit()
            #     print("finish execute", event.status)
            # else:
            heapq.heappush(self._queue, EventWrapper(event))

        print("FINISHED RECOVERY")

    async def _run_loop(self):
        while self.running:
            if not self._queue:  # pq is empty
                print("waiting")
                await asyncio.sleep(1)
                continue

            next_event = self._queue[0]
            if next_event.execution_time > datetime.now():
                print("waiting")
                await asyncio.sleep(next_event.execution_time - datetime.now())

            event = heapq.heappop(self._queue)
            await self._execute_event(event)

    async def _execute_event(self, event: TickEvent):
        try:
            # assume tickevent

            # call RpMetaService to initate update,
            # and retrieve a new Event for insertion
            await self.rp_meta_service.initiate_rp_tickover(event)

            event.status = "completed"
            print(event.status, event.id)
            print(self._session.dirty)
            self._session.commit()
            print(event)
        except Exception as e:
            event.status = "failed"
            logging.error("Event execution failed", e)
        finally:
            # commit status update
            self._session.commit()

    # ==== EVENT GETTERS =====
    # def get_events_for_rp(self, rp_id: int):
    #     if not self._queue:
    #         return []
    #     return [event for event in self._queue if event.rp_id == rp_id]


class EventWrapper:
    def __init__(self, event: TickEvent):
        self._event = event

    def __lt__(self, other):
        # custom comparator for heap pqueue
        return self._event.execution_time < other._event.execution_time

    def __getattr__(self, name):
        # pass methods/atttributes from internal class
        return getattr(self._event, name)
