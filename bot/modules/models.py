from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    history_access: Mapped[bool] = mapped_column(default=False)
    traffic_access: Mapped[bool] = mapped_column(default=False)
    requests_access: Mapped[bool] = mapped_column(default=False)

    traffic: Mapped[List["ClientTraffic"]] = relationship(back_populates = "client")
    history: Mapped[List["ClientHistory"]] = relationship(back_populates = "client")
    requests: Mapped[List["ClientRequests"]] = relationship(back_populates = "client")
    client_temp_selection: Mapped[List["ClientsTempSelection"]] = relationship(back_populates = "client")

    def __repr__(self):
        return f"Client(id={self.id}, email='{self.email}', history_access={self.history_access}, " \
               f"traffic_access={self.traffic_access}, requests_access={self.requests_access})"


class ClientTraffic(Base):
    __tablename__ = "client_traffic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    bytes_sent: Mapped[int] = mapped_column(default=0)
    bytes_received: Mapped[int] = mapped_column(default=0)

    client: Mapped[Client] = relationship(back_populates = "traffic")

    def __repr__(self):
        return f"ClientTraffic(id={self.id}, user_id={self.user_id}, start_time={self.start_time}, " \
               f"end_time={self.end_time}, bytes_sent={self.bytes_sent}, bytes_received={self.bytes_received})"


class ClientHistory(Base):
    __tablename__ = "client_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement = True)
    user_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    site_url: Mapped[str]
    last_visit_time: Mapped[datetime]
    count: Mapped[int] = mapped_column(default=1)

    client: Mapped[Client] = relationship(back_populates = "history")

    def __repr__(self):
        return f"ClientHistory(id={self.id}, user_id={self.user_id}, site_url='{self.site_url}', " \
               f"last_visit_time={self.last_visit_time}, count={self.count})"


class ClientRequests(Base):
    __tablename__ = "client_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    requests_count: Mapped[int] = mapped_column(default=0)

    client: Mapped[Client] = relationship(back_populates = "requests")

    def __repr__(self):
        return f"ClientRequests(id={self.id}, user_id={self.user_id}, start_time={self.start_time}, " \
               f"end_time={self.end_time}, requests_count={self.requests_count})"


class ClientsTempSelection(Base):
    __tablename__ = "clients_temp_selection"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement = True)
    admin_id: Mapped[int]
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    number: Mapped[int]

    client: Mapped[Client] = relationship(back_populates = "client_temp_selection")