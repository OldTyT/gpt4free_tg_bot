"""Sample worker with multiprocessing."""
import multiprocessing
import os
import sys

from pydantic import SecretStr
from redis import Redis  # noqa: I201,I100
from rq import Connection, Worker  # noqa: I201,I100

from logger import logger  # noqa: I201,I100


def num_workers_needed():
    """Geting max num workers."""
    return int(os.getenv("MAX_NUM_WORKERS", 10))


def start_rq_worker():
    """Start rq worker with multiprocessing."""
    try:
        redis_conn = Redis(
            host=str(os.getenv("REDIS_HOST", "localhost")),
            password=SecretStr(os.getenv("REDIS_AUTH", "")),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DATABASE", 0)),
        )
        with Connection(connection=redis_conn):
            qs = sys.argv[1:] or "fast_gpt4_bot_queue"
            for i in range(num_workers_needed()):
                multiprocessing.Process(
                    target=Worker(qs).work, kwargs={"with_scheduler": True}
                ).start()
                logger.info(f"Worker process id: {i} started!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_rq_worker()
