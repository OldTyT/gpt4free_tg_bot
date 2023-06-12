import os
import logging  # noqa F401
import logger  # noqa F401
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from redis import Redis
from pydantic import SecretStr
from rq import Queue, Retry
from loguru import logger as my_logger

from models.runtime import RuntimeSettings
from jobs import GenerateTextWithGPTModel
from proxy import ProxyMessage


bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)
pm = ProxyMessage()


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


def prompt_gpt4_start(prompt, chat_id):
    my_logger.debug(f"Setup gpt4_prompt_job. Chat id: {chat_id}. Prompt: {prompt}")
    state_cfg.rq_queue.enqueue(
        GenerateTextWithGPTModel,
        chat_id=chat_id,
        prompt=prompt,
        tg_bot_token=SecretStr(os.getenv("TELEGRAM_BOT_TOKEN")),
        job_timeout=120,
        retry=Retry(max=3)
    )


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if pm.check(message):
        msg_start = "GPT4 FastBot\n" \
                    "\n" \
                    "Ask me something. Or use cmd `/gen <something>`."
        my_logger.debug(f"Starting for chat id: {message.chat.id}")
        await message.answer(msg_start, parse_mode="Markdown")


@dp.message_handler(commands=['ping'])
async def message_ping_cmd(message: types.Message):
    if pm.check(message):
        await message.answer("pong")


@dp.message_handler(commands=['gen'])
async def message_gen_cmd(message: types.Message):
    if pm.check(message):
        if len(message.text) < 5:
            await message.answer(f"The text is very short.")
            return
        prompt_gpt4_start(
            prompt=message.text[5:],  # remove '/gen ' from msg
            chat_id=message.chat.id
        )


@dp.message_handler()
async def all_message_handler(message: types.Message):
    if pm.check(message):
        prompt_gpt4_start(prompt=message.text, chat_id=message.from_user.id)


if __name__ == '__main__':
    executor.start_polling(dp)
