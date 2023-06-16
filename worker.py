import os
import sys
import multiprocessing

from rq import Connection, Worker
from redis import Redis
from pydantic import SecretStr

from logger import logger


def num_workers_needed():
    return int(os.getenv("MAX_NUM_WORKERS", 10))


def start_rq_worker():
    try:
        redis_conn = Redis(
            host=str(os.getenv("REDIS_HOST", "localhost")),
            password=SecretStr(os.getenv("REDIS_AUTH", "")),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DATABASE", 0))
        )
        with Connection(connection=redis_conn):
            qs = sys.argv[1:] or 'fast_gpt4_bot_queue'
            for i in range(num_workers_needed()):
                multiprocessing.Process(target=Worker(qs).work, kwargs={'with_scheduler': True}).start()
    except Exception as e:
        logger.error("Fatal error: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    start_rq_worker()
