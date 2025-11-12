import datetime
from typing import List

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Interval,
    String,
    Table,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidderbot.services.database import Base

"""
https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
"""


# (n,n) relationship
server_rp_table = Table(
    "server_rp_table",
    Base.metadata,
    Column("server_id", ForeignKey("servers.id"), primary_key=True),
    Column("rp_id", ForeignKey("rps.id"), primary_key=True),
)


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    server_rps: Mapped[List["Rp"]] = relationship(
        secondary=server_rp_table, back_populates="rp_servers"
    )


class Rp(Base):
    __tablename__ = "rps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    universe_name: Mapped[str] = mapped_column()
    is_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)

    curr_time_rp: Mapped[datetime.datetime] = mapped_column(nullable=False)

    tickinterval_rp: Mapped[datetime.timedelta] = mapped_column(nullable=False)
    tickinterval_real: Mapped[datetime.timedelta] = mapped_column(nullable=False)

    update_channel_id: Mapped[int] = mapped_column(BigInteger)

    rp_servers: Mapped[List["Server"]] = relationship(
        secondary=server_rp_table, back_populates="server_rps"
    )


class TickEvent(Base):
    __tablename__ = "tick_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="pending")

    rp_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("rps.id", ondelete="CASCADE", onupdate="CASCADE"),
    )


# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
#     name: Mapped[str] = mapped_column(nullable=False)


# class Object(Base):
#     __tablename__ = "objects"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(
#         BigInteger, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE")
#     )
#     value: Mapped[int] = mapped_column()
