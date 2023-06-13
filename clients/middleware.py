import json
import asyncio

from pydantic import BaseSettings

from models.history import MessageHistory
from db.base import get_session
from logger import logger


class MessagesSaver(BaseSettings):
    def save_msg(self, message):
        loop = asyncio.get_event_loop()
        coroutine = self.save_message(message)
        loop.run_until_complete(coroutine)

    async def save_message(self, message):
        session = [session_q async for session_q in get_session()][0]
        logger.debug(message)
        message_h = MessageHistory(message=json.loads(str(message)))
        session.add(message_h)
        try:
            await session.commit()
            return True
        except Exception as ex:
            await session.rollback()
            logger.error(ex)
            return False
