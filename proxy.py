from sqlalchemy import select
from rq import Retry

from loguru import logger
from models.users import Users  # noqa: F401
from db.base import get_session
from models.cofigs import GlobalConfigs
from jobs import SaveMessage

cfg = GlobalConfigs()


class ProxyMessage:
    async def cmd_start(self, message):
        session = [session_q async for session_q in get_session()][0]
        user = await session.execute(select(Users).where(Users.user_id == message.from_user.id))
        user = user.scalars().all()
        if not user:
            user = Users(
                user_id=message.from_user.id,
                first_name=message.from_user.first_name,
                username=message.from_user.username,
                last_name=message.from_user.last_name
            )
            session.add(user)
            try:
                await session.commit()
                return True
            except Exception as ex:
                await session.rollback()
                logger.error(ex)
                return False
        return True

    async def check(self, message):
        cfg.state_cfg.rq_queue.enqueue(
            SaveMessage,
            message=message,
            job_timeout=120,
            retry=Retry(max=3)
        )
        return True
