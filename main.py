import os
import asyncio
import logging
import logger
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from redis import Redis
from pydantic import SecretStr
from rq import Queue
#from aiogram.enums.parse_mode import ParseMode
# from aiogram.fsm.storage.memory import MemoryStorage

from models.runtime import RuntimeSettings
from jobs import GenerateTextWithGPTModel


bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)

redis_conn = Redis(
    host = str(os.getenv("REDIS_HOST", "localhost")),
    password = SecretStr(os.getenv("REDIS_AUTH", "")),
    port = int(os.getenv("REDIS_PORT", 6379)),
    db = int(os.getenv("REDIS_DATABASE", 0))
)

state_cfg = RuntimeSettings(
    redis_conn=redis_conn,
    rq_queue=Queue(os.getenv("REDIS_QUEUE", "fast_gpt4_bot_queue"), connection=redis_conn),
    started_at=datetime.now(timezone.utc),
    last_update=datetime.fromtimestamp(0)
)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer("Hello! I'm GPT 4 language model")

@dp.message_handler()
async def message_handler(message: types.Message):
    gpt4_prompt_job = state_cfg.rq_queue.enqueue(
        GenerateTextWithGPTModel,
        chat_id=message.from_user.id,
        prompt=message.text,
        tg_bot_token=SecretStr(os.getenv("TELEGRAM_BOT_TOKEN")),
        result_ttl=3600
    )
    await message.answer(f"Wait please...")

if __name__ == '__main__':
    executor.start_polling(dp)
