import os
from datetime import datetime, timezone

from redis import Redis
from rq import Queue
from pydantic import SecretStr

from models.runtime import RuntimeSettings


class GlobalConfigs:
    redis_conn = Redis(
        host=str(os.getenv("REDIS_HOST", "localhost")),
        password=SecretStr(os.getenv("REDIS_AUTH", "")),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DATABASE", 0))
    )
    state_cfg = RuntimeSettings(
        redis_conn=redis_conn,
        rq_queue=Queue(os.getenv("REDIS_QUEUE", "fast_gpt4_bot_queue"), connection=redis_conn),
        started_at=datetime.now(timezone.utc),
        last_update=datetime.fromtimestamp(0)
    )
    telegram_token_bot = SecretStr(os.getenv("TELEGRAM_BOT_TOKEN"))
