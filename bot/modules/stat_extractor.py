from datetime import datetime, UTC, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.modules.models import Client, ClientHistory, ClientTraffic, ClientsTable
from bot.modules.v2ray import get_stats, NoStatsAvailable
from bot.modules.logger import get_logger


logger = get_logger(__name__)


async def get_clients(stats: list[dict[str, str | int]],
                      session: AsyncSession) -> dict[Client, dict[str, str | int]]:
    """Convert v2ray stats into dict of Clients and information dicts

    If client isn't registered in the bot, he won't be in dict
    Information dict contains two keys: "uplink" and "downlink" (in bytes)

    :param stats: List of v2ray stats dicts
    :param session: SQLAlchemy async session

    :return: Dict of Clients
    """
    clients = {}
    for item in stats:
        name = item["target"]
        client = await session.scalar(select(Client).where(Client.email == name))
        if client is None:
            continue
        if name not in clients:
            clients[client] = {}
        if "uplink" in item and "uplink" not in clients[client]:
            clients[client]["uplink"] = item["value"]
        if "downlink" in item and "downlink" not in clients[client]:
            clients[client]["downlink"] = item["value"]
    return clients


async def save_stats(stats: list[dict[str, str | int]], current_time: datetime, session: AsyncSession) -> None:
    """Save v2ray stats into the database.

    :param stats: List of v2ray stats dicts
    :param current_time: The time, when the stats were obtained.
    :param session: SQLAlchemy async session
    """
    for item in stats:
        direction, target, type_, value = item["direction"], item["target"], item["type"], item["value"]
        stmt = (
            select(ClientsTable)
            .where(ClientsTable.direction == direction)
            .where(ClientsTable.target == target)
            .where(ClientsTable.type == type_)
        )
        old_record = await session.scalar(stmt)
        if old_record is None:
            record = ClientsTable(
                direction = item["direction"],
                target = item["target"],
                type = item["type"],
                value = item["value"],
                last_updated = current_time
            )
            session.add(record)
        else:
            old_record.last_updated = current_time
    await session.commit()


async def update_traffic_info(clients: dict[Client, dict[str, str | int]],
                              current_time: datetime,
                              session: AsyncSession) -> None:
    """Update the traffic info table.

    :param clients: Dict of Clients and info dicts
    :param current_time: The time, when the stats were obtained.
    :param session: SQLAlchemy async session
    """
    for client, info in clients.items():
        if not client.traffic_access:
            continue
        stmt = select(ClientsTable).where(ClientsTable.target == Client.email)
        downlink = await session.scalar(stmt.where(ClientsTable.type == "downlink"))
        uplink = await session.scalar(stmt.where(ClientsTable.type == "uplink"))

        if downlink is None or uplink is None:
            continue

        start_time = downlink.last_updated + timedelta(seconds=1)
        bytes_sent, bytes_received = uplink.value - info["uplink"], downlink.value - info["downlink"]
        new_record = ClientTraffic(
            client = client,
            start_time = start_time,
            end_time = current_time,
            bytes_sent = bytes_sent,
            bytes_received = bytes_received,
        )
        session.add(new_record)
        await session.commit()


async def extract_stats(sessionmaker: async_sessionmaker[AsyncSession], api_server: str) -> None:
    """Extract and save stats every X minutes.

    :param sessionmaker: SQLAlchemy async session
    :param api_server: V2Ray API server
    """
    async with sessionmaker() as session:
        try:
            stats, time = get_stats(api_server), datetime.now(UTC)
        except NoStatsAvailable:
            return
        clients = await get_clients(stats, session)
        await update_traffic_info(clients, time, session)
        await save_stats(stats, time, session)


def setup_scheduler(sessionmaker: async_sessionmaker[AsyncSession], api_server: str) -> AsyncIOScheduler:
    """Sets up the scheduler and return it.

    :param sessionmaker: SQLAlchemy async session
    :param api_server: V2Ray API server

    :return: AsyncIOScheduler
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        extract_stats,
        args = (sessionmaker, api_server),
        trigger="cron",
        minute="0,10,20,30,40,50",
        second="0",
    )
    scheduler.start()
    return scheduler
