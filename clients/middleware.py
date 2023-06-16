import json
import asyncio

from pydantic import BaseSettings

from models.history import MessageHistory, CallbackQueryHistory
from db.base import get_session
from logger import logger


class MessagesSaver(BaseSettings):
    def save_msg(self, message):
        loop = asyncio.get_event_loop()
        coroutine = self.save_message(message)
        loop.run_until_complete(coroutine)
        return True

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


class CallbackQuerySaver(BaseSettings):
    def save_qc(self, callback_query):
        loop = asyncio.get_event_loop()
        coroutine = self.save_callback_query(callback_query)
        loop.run_until_complete(coroutine)
        return True

    async def save_cq(self, callback_query):
        session = [session_q async for session_q in get_session()][0]
        logger.debug(callback_query)
        callback_query_h = CallbackQueryHistory(callback_query=json.loads(str(callback_query)))
        session.add(callback_query_h)
        try:
            await session.commit()
            return True
        except Exception as ex:
            await session.rollback()
            logger.error(ex)
            return False
