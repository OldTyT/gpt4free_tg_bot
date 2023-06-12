import json

import jsonpickle

from loguru import logger
from models.users import Users  # noqa: F401
from models.history import MessageHistory
from db.base import get_session


class ProxyMessage:
    async def check(self, message):
        session = [session_q async for session_q in get_session()][0]
        logger.debug(message)
        message_h = MessageHistory(message=json.loads(jsonpickle.encode(message)))
        session.add(message_h)
        try:
            await session.commit()
            return True
        except Exception as ex:
            await session.rollback()
            logger.error(ex)
            return False
