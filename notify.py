# Need refactor.
import asyncio
import os
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from sqlalchemy import select

from db.base import get_session
from logger import logger
from models.configs import GlobalConfigs
from models.history import Chats

cfg = GlobalConfigs()
bot = Bot(token=cfg.telegram_token_bot.get_secret_value())


def main():
    loop = asyncio.get_event_loop()
    coroutine = main_async()
    loop.run_until_complete(coroutine)
    return True


async def send_message_inactive_chats(chats: list):
    for chat in chats:
        try:
            await bot.send_message(chat, cfg.inactive_message, parse_mode="Markdown")
            logger.info(f"Successfully notify for chat_id: {chat}")
        except Exception as e:
            logger.error("Fatal error: {}".format(e))
    return True


async def get_inactive_chats():
    session = [session_q async for session_q in get_session()][0]
    chats = await session.execute(
        select(Chats).where(
            Chats.message_last_time
            < (datetime.now(timezone.utc) - timedelta(days=cfg.inactive_days))
        )
    )  # noqa E501
    chats_inactive = []
    chats = chats.scalars().all()
    for chat in chats:
        chats_inactive.append(chat.chat_id)
    await session.close()
    return chats_inactive


async def main_async():
    chats = await get_inactive_chats()
    if await send_message_inactive_chats(chats):
        return
    os.exit(1)


main()
