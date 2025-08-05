from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    history_access: Mapped[bool] = mapped_column(default=False)
    traffic_access: Mapped[bool] = mapped_column(default=False)
    stats_access: Mapped[bool] = mapped_column(default=False)

    history = relationship("ClientHistory", backref= "client")
    traffic = relationship("ClientTraffic", backref= "client")
    requests = relationship("ClientRequests", backref="client")

    def __repr__(self):
        return f"Client(id={self.id}, email='{self.email}', history_access={self.history_access}, " \
               f"traffic_access={self.traffic_access}, stats_access={self.stats_access})"


class ClientHistory(Base):
    __tablename__ = "client_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    site_url: Mapped[str]
    last_visit_time: Mapped[datetime]
    count: Mapped[int] = mapped_column(default=1)

    def __repr__(self):
        return f"ClientHistory(id={self.id}, user_id={self.user_id}, site_url='{self.site_url}', " \
               f"last_visit_time={self.last_visit_time}, count={self.count})"


class ClientTraffic(Base):
    __tablename__ = "client_traffic"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    bytes_sent: Mapped[int] = mapped_column(default=0)
    bytes_received: Mapped[int] = mapped_column(default=0)

    def __repr__(self):
        return f"ClientTraffic(id={self.id}, user_id={self.user_id}, start_time={self.start_time}, " \
               f"end_time={self.end_time}, bytes_sent={self.bytes_sent}, bytes_received={self.bytes_received})"


class ClientRequests(Base):
    __tablename__ = "client_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    requests_count: Mapped[int] = mapped_column(default=0)

    def __repr__(self):
        return f"ClientRequests(id={self.id}, user_id={self.user_id}, start_time={self.start_time}, " \
               f"end_time={self.end_time}, requests_count={self.requests_count})"
