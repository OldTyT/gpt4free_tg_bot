"""GPT generate clients."""
import time
from threading import Thread

import telebot
from pydantic import BaseSettings

import g4f
from logger import logger
from models.configs import GlobalConfigs

stop_typing = False
cfg = GlobalConfigs()
bot = telebot.TeleBot(cfg.telegram_token_bot.get_secret_value())

IGNORE_ERRORS = [  # Hardcode, need refactor
    "A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message"  # noqa E501
]


def set_is_typing(chat_id):
    """Set bot status typing."""
    while True:
        if stop_typing:
            return
        logger.debug(f"stop_typing is False. Seting status typing. Chat id: {chat_id}")
        bot.send_chat_action(chat_id, action="typing")
        time.sleep(4)


def get_full_len_list(my_list: list):
    """Get full len list."""
    cnt = 0
    for i in my_list:
        cnt += len(i)
    return cnt


def get_str_from_list(my_list: list):
    """Get string from list."""
    return "".join(str(x) for x in my_list)


class GPT4TextGenerate(BaseSettings):
    """GPT4TextGenerate class."""

    def message_responser(self, prompt, chat_id, msg_id):
        """Set typing bot status and generate text."""
        if chat_id != 0:
            Thread(target=set_is_typing, args=(chat_id,)).start()
        result_generate = self.gpt4_generate(
            prompt=prompt, chat_id=chat_id, msg_id=msg_id
        )
        if result_generate:
            stop_typing = True
            logger.debug(f"Result sent successful for chat id: {chat_id}")
            return True
        stop_typing = True  # noqa F841
        self.send_message("Smth error", chat_id)
        raise RuntimeError

    def gpt4_generate(self, chat_id, prompt, msg_id):  # noqa: CFQ004,CFQ001
        """Generate text with prompt and send."""
        prompt = cfg.pre_prompt + prompt
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            provider=g4f.Provider.DeepAi,
            stream=True
        )
        full_text = []
        max_length = 150
        number_divisions = 1
        cnt_divisions = 1
        len_list = 0
        last_len_list = 0
        for i in response:
            full_text.append(i)
            if get_full_len_list(full_text) / (max_length * number_divisions) > 1:
                number_divisions += 1
                if get_full_len_list(full_text) / ((4096 - max_length) * cnt_divisions) >= 1:
                    logger.debug("Len message to long. Send new message.")
                    if chat_id == 0:
                        return True
                    msg_id = self.send_message(
                        text=get_str_from_list(full_text[last_len_list:]),
                        chat_id=chat_id,
                    )
                    len_list = len(full_text)
                    cnt_divisions += 1
                else:
                    if chat_id != 0:
                        try:
                            bot.edit_message_text(
                                chat_id=chat_id,
                                text=get_str_from_list(full_text[len_list:]),
                                message_id=msg_id,
                            )
                            last_len_list = len(full_text)
                            if chat_id == 0:
                                bot.edit_message_text(
                                    inline_message_id=msg_id,
                                    text=get_str_from_list(full_text[len_list:]),
                                )
                        except telebot.apihelper.ApiTelegramException as e:
                            if str(e) in IGNORE_ERRORS:
                                pass
                            else:
                                raise RuntimeError(e)
        try:
            if len(get_str_from_list(full_text[len_list:])) > 0:
                if chat_id == 0:
                    bot.edit_message_text(
                        inline_message_id=msg_id,
                        text=get_str_from_list(full_text[len_list:]),
                    )
                    return True
                bot.edit_message_text(
                    chat_id=chat_id,
                    text=get_str_from_list(full_text[len_list:]),
                    message_id=msg_id,
                )
        except telebot.apihelper.ApiTelegramException as e:
            if str(e) in IGNORE_ERRORS:
                return True
            raise RuntimeError(e)
        return True

    def send_message(self, text, chat_id):
        """Send message with chunk per 4096 sumbol."""
        max_length = 4096
        chunks = [text[i: i + max_length] for i in range(0, len(text), max_length)]
        msg_id = 0
        try:
            for chunk in chunks:
                if chat_id == 0:
                    return True
                msg_id = bot.send_message(chat_id, chunk).message_id
            return msg_id
        except telebot.apihelper.ApiTelegramException as e:
            if str(e) in IGNORE_ERRORS:
                return msg_id
            raise RuntimeError(e)
