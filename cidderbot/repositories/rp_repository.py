from sqlalchemy import select

from cidderbot.models.models import Rp, Server


class RpRepository:
    def __init__(self, session):
        self._session = session

    """
    Currently not going to support C_UD, only R ops :)
    """

    def get_all_rps(self) -> list[Rp]:
        session = self._session
        try:
            rps = session.execute(select(Rp))
            return rps
        finally:
            session.close()

    def get_rps_of_server(self, server_id: int) -> list[Rp]:
        session = self._session
        try:
            stmt = select(Rp).where(Rp.rp_servers.any(Server.id == server_id))
            rps = session.scalars(stmt).all()  # only 1 entity, use scalars()

            return rps
        finally:
            session.close()

    def get_rp_by_id(self, rp_id: int) -> Rp:
        session = self._session
        try:
            return session.query(Rp).filter(Rp.id == rp_id).first()
        finally:
            session.close()
