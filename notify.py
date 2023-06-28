import asyncio
from datetime import datetime, timezone, timedelta

from aiogram import Bot
from sqlalchemy import select

from models.configs import GlobalConfigs
from models.history import Chats
from db.base import get_session
from logger import logger

cfg = GlobalConfigs()
bot = Bot(token=cfg.telegram_token_bot.get_secret_value())


def main():
    loop = asyncio.get_event_loop()
    coroutine = get_inactive_chats()
    loop.run_until_complete(coroutine)
    return True


async def send_message_inactive_chats(chats: list):
    for chat in chats:
        try:
            await bot.send_message(chat, cfg.inactive_message, parse_mode="Markdown")
            logger.info(f"Successfully notify for chat_id: {chat}")
        except Exception as e:
            logger.error("Fatal error: {}".format(e))


async def get_inactive_chats():
    session = [session_q async for session_q in get_session()][0]
    chats = await session.execute(select(Chats).where(Chats.message_last_time < (datetime.now(timezone.utc) - timedelta(days=cfg.inactive_days))))  # noqa E501
    chats_inactive = []
    chats = chats.scalars().all()
    for chat in chats:
        chats_inactive.append(chat.chat_id)
        await send_message_inactive_chats(chats_inactive)

main()
