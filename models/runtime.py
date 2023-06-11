from datetime import datetime
from redis import Redis
from rq import Queue
from pydantic import BaseSettings, SecretStr


class RuntimeSettings(BaseSettings):
    redis_conn: Redis
    rq_queue: Queue
    started_at: datetime
    last_update: datetime
