import io
from datetime import datetime, timedelta, UTC

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from matplotlib import pyplot as plt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.modules.logger import get_logger
from bot.modules.models import Client, ClientTraffic

logger = get_logger(__name__)

router = Router()


async def generate_traffic_chart(start_dt: datetime,
                                 end_dt: datetime,
                                 session: AsyncSession,
                                 client: type[Client]) -> io.BytesIO:
    stmt = (
        select(ClientTraffic)
        .where(ClientTraffic.client == client)
        .where(ClientTraffic.start_time >= start_dt)
        .where(ClientTraffic.end_time <= end_dt)
        .order_by(ClientTraffic.start_time)
    )
    traffics = await session.scalars(stmt)
    if not traffics:
        raise ValueError("There is no traffic data between the start and end time")

    times = [traffic.start_time for traffic in traffics]
    received = [traffic.bytes_received for traffic in traffics]
    sent = [traffic.bytes_sent for traffic in traffics]

    plt.figure(figsize = (10, 6))
    plt.plot(times, received, label = "Received (bytes)", color = "blue")
    plt.plot(times, sent, label = "Sent (bytes)", color = "green")
    plt.title("Traffic Stats")
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format = "png")
    plt.close()
    buf.seek(0)
    return buf


@router.message(F.text == "Traffic 📈")
async def traffic_handler(message: Message, session: AsyncSession) -> None:
    logger.info(f"Received `Traffic` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    client = await session.get(Client, message.from_user.id)
    if client is None:
        await message.answer("You're not a client.")
        return
    if not client.traffic_access:
        await message.answer("You don't granted access to the traffic in /policy")
        return
    try:
        end_dt = datetime.now(UTC)
        start_dt = end_dt - timedelta(hours = 1)

        img_buf = await generate_traffic_chart(start_dt, end_dt, session, client)
        input_file = BufferedInputFile(img_buf.read(), filename = "traffic.png")
        await message.answer_photo(photo = input_file, caption = f"Трафик с {start_dt} по {end_dt}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(F.text == "History 📜")
async def history_handler(message: Message, session: AsyncSession) -> None:
    logger.info(f"Received `History` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    access = (await session.get(Client, message.from_user.id)).history_access
    if not access:
        await message.answer("You don't granted access to the history in /policy")
        return
    await message.answer("Not implemented yet :))")


@router.message(F.text == "Requests's count 📈")
async def requests_handler(message: Message, session: AsyncSession) -> None:
    logger.info(f"Received `Requests's count` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    access = (await session.get(Client, message.from_user.id)).requests_access
    if not access:
        await message.answer("You don't granted access to the requests in /policy")
        return
    await message.answer("Not implemented yet :)))")
