import logging

from sqlalchemy import select

from cidderbot.models.models import TickEvent


class EventRepository:
    def __init__(self, session):
        self._session = session

    """
    Required operations:
    * [V] Get all currently pending events
    * [ ] Remove event (id) - not supporting, 
        just set status=completed and call session.commit()
    * [V] Add event
    """

    def add_tick_event(self, event: TickEvent):
        session = self._session
        try:
            session.add(event)
            session.commit()
            session.refresh(event)
            logging.info("Created event: %s", event)

            return event
        except Exception as e:
            session.rollback()
            logging.error(f"Adding event", e)
        finally:
            session.close()

    def get_pending_events(self):
        session = self._session

        try:
            stmt = select(TickEvent).where(TickEvent.status == "pending")
            events = session.scalars(stmt).all()  # only 1 entity
            return events
        finally:
            session.close()

    # def get_rps_of_server(self, server_id: int):
    #     session = self._session
    #     try:
    #         stmt = select(Rp).where(Rp.servers.any(Server.id == server_id))
    #         rps = session.scalars(stmt).all()

    #         return rps
    #     finally:
    #         session.close()

    # def get_rp_by_id(self, rp_id: int):
    #     session = self._session
    #     try:
    #         return session.query(Rp).filter(Rp.id == rp_id).first()
    #     finally:
    #         session.close()

    # def delete_object(self, id: int):
    #     session = self._session
    #     try:
    #         obj = session.query(Object).filter(Object.id == id).first()
    #         if obj:
    #             session.delete(obj)
    #             session.commit()
    #             print(f"Deleted: {obj}")
    #         else:
    #             print("Object not found.")
    #     finally:
    #         session.close()
