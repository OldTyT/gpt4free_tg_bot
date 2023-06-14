import logging  # noqa F401
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from rq import Retry
import logger  # noqa F401
from loguru import logger as my_logger
from rq import Queue
from redis import Redis

from models.configs import GlobalConfigs
from jobs import GenerateTextWithGPTModel
from proxy import ProxyMessage, ProxyCallbackQuery
from models.runtime import RuntimeSettings

logging.getLogger().setLevel(logging.DEBUG)
cfg = GlobalConfigs()
bot = Bot(token=cfg.telegram_token_bot.get_secret_value())
dp = Dispatcher(bot)
pm = ProxyMessage()
pcb = ProxyCallbackQuery()

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

prompt_callback = CallbackData("prompt", "something")


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
            await dp.bot.set_my_commands([
                types.BotCommand("ping", "Pong"),
                types.BotCommand("gen", "Text generation. Ex.: /gen <something>"),
            ])
            msg_start = "Hello! I'm fastest GPT bot\n" \
                        "\n" \
                        "Ask me something. Or use cmd `/gen <something>`."
            await message.answer(msg_start, parse_mode="Markdown")


@dp.message_handler(commands=['ping'])
async def message_ping_cmd(message: types.Message):
    await message.answer("pong")


@dp.message_handler(commands=['gen'])
async def message_gen_cmd(message: types.Message):
    if await pm.check(message):
        if message.text.find(" ") == -1:
            await message.answer("The text is very short.")
            return
        prompt = message.text[message.text.find(" ")+1:]  # remove '/gen ' from msg
        if len(prompt) < 1:
            await message.answer("The text is very short.")
            return
        msg_id = await message.answer("Wait please...")
        msg_id = msg_id.message_id
        prompt_gpt4_start(
            prompt=prompt,
            chat_id=message.chat.id,
            msg_id=msg_id
        )


@dp.message_handler()
async def all_message_handler(message: types.Message):
    if await pm.check(message):
        msg_id = await message.answer("Wait please...")
        msg_id = msg_id.message_id
        prompt_gpt4_start(prompt=message.text, chat_id=message.chat.id, msg_id=msg_id)


@dp.inline_handler()
async def inline_general_handler(inline_query: InlineQuery):
    prompt = inline_query.query or 'something'
    prompt_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Generate",
                    callback_data=prompt_callback.new(
                        prompt,
                    )
                ),
            ]
        ]
    )
    item = InlineQueryResultArticle(
            id=1,
            description='Send message for generate text from this prompt.',
            title=prompt,
            reply_markup=prompt_kb,
            input_message_content=InputTextMessageContent(
                'Please click on the button.',
                parse_mode=types.ParseMode.HTML
            )
    )
    await bot.answer_inline_query(
        inline_query.id,
        results=[item],
        cache_time=1,
        switch_pm_parameter="from_inline_prompt_generate",
        switch_pm_text="Back to bot."
    )


@dp.callback_query_handler(prompt_callback.filter())
async def process_callback_prompt_generate(callback_query: types.CallbackQuery):
    if await pcb.check(callback_query):
        prompt = callback_query.data[callback_query.data.find(":")+1:]
        prompt_gpt4_start(
            prompt=prompt,
            chat_id=0,
            msg_id=callback_query.inline_message_id
        )
        await bot.edit_message_text(
            inline_message_id=callback_query.inline_message_id,
            text="Please wait...",
            parse_mode=types.ParseMode.HTML
        )


if __name__ == '__main__':
    executor.start_polling(dp)
