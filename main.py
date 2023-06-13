import logging  # noqa F401
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from rq import Retry
import logger  # noqa F401
from loguru import logger as my_logger
from rq import Queue
from redis import Redis

from models.configs import GlobalConfigs
from jobs import GenerateTextWithGPTModel
from proxy import ProxyMessage
from models.runtime import RuntimeSettings

logging.getLogger().setLevel(logging.DEBUG)
cfg = GlobalConfigs()
bot = Bot(token=cfg.telegram_token_bot.get_secret_value())
dp = Dispatcher(bot)
pm = ProxyMessage()

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


def prompt_gpt4_start(prompt, chat_id, msg_id):
    my_logger.debug(f"Setup gpt4_prompt_job. Chat id: {chat_id}. Prompt: {prompt}")
    state_cfg.rq_queue.enqueue(
        GenerateTextWithGPTModel,
        chat_id=chat_id,
        prompt=prompt,
        tg_bot_token=cfg.telegram_token_bot,
        msg_id=msg_id,
        job_timeout=120,
        retry=Retry(max=3)
    )


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if await pm.cmd_start(message):
        if await pm.check(message):
            msg_start = "GPT4 FastBot\n" \
                        "\n" \
                        "Ask me something. Or use cmd `/gen <something>`."
            await message.answer(msg_start, parse_mode="Markdown")


@dp.message_handler(commands=['ping'])
async def message_ping_cmd(message: types.Message):
    await message.answer("pong")


@dp.message_handler(commands=['gen'])
async def message_gen_cmd(message: types.Message):
    if await pm.check(message):
        if len(message.text) < 5:
            await message.answer("The text is very short.")
            return
        msg_id = await message.answer("Wait please...")
        msg_id = msg_id.message_id
        prompt_gpt4_start(
            prompt=message.text[5:],  # remove '/gen ' from msg
            chat_id=message.chat.id,
            msg_id=msg_id
        )


@dp.message_handler()
async def all_message_handler(message: types.Message):
    if await pm.check(message):
        msg_id = await message.answer("Wait please...")
        msg_id = msg_id.message_id
        prompt_gpt4_start(prompt=message.text, chat_id=message.from_user.id, msg_id=msg_id)


if __name__ == '__main__':
    executor.start_polling(dp)
