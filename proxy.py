from datetime import datetime, timezone

from sqlalchemy import select
from rq import Retry, Queue
from redis import Redis

from loguru import logger
from models.users import Users  # noqa: F401
from db.base import get_session
from models.configs import GlobalConfigs
from jobs import SaveMessage, SaveCallbackQuery, UpdateLastTime
from models.runtime import RuntimeSettings

cfg = GlobalConfigs()

redis_conn = Redis(
    host=cfg.redis_host,
    password=cfg.redis_password.get_secret_value(),
    port=cfg.redis_port,
    db=cfg.redis_db
)

state_cfg = RuntimeSettings(
    redis_conn=redis_conn,
    rq_queue=Queue("fast_gpt4_bot_queue", connection=redis_conn),
    started_at=datetime.now(timezone.utc),
    last_update=datetime.fromtimestamp(0)
)


class ProxyCallbackQuery:
    async def check(self, callback_query):
        state_cfg.rq_queue.enqueue(
            SaveCallbackQuery,
            callback_query=str(callback_query),
            job_timeout=10,
            retry=Retry(
                max=5,
                interval=1
            )
        )
        return True


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
        state_cfg.rq_queue.enqueue(
            SaveMessage,
            message=str(message),
            job_timeout=10,
            retry=Retry(
                max=5,
                interval=1
            )
        )
        state_cfg.rq_queue.enqueue(
            UpdateLastTime,
            time=datetime.now(timezone.utc),
            chat_id=message.chat.id,
            job_timeout=10,
            retry=Retry(
                max=5,
                interval=1
            )
        )
        return True
