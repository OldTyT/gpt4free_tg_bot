import time
from threading import Thread

import telebot
from pydantic import BaseSettings

import g4f
from logger import logger


STOP_TYPING = False


def set_is_typing(chat_id, tg_bot_token):
    bot = telebot.TeleBot(tg_bot_token.get_secret_value())
    while True:
        if STOP_TYPING:
            return
        logger.debug(f"STOP_TYPING is False. Seting status typing. Chat id: {chat_id}")
        bot.send_chat_action(chat_id, action="typing")
        time.sleep(4)


def get_full_len_list(my_list: list):
    cnt = 0
    for i in my_list:
        cnt += len(i)
    return cnt


def get_str_from_list(my_list: list):
    return ''.join(str(x) for x in my_list)


class GPT4TextGenerate(BaseSettings):

    def message_responser(self, prompt, chat_id, tg_bot_token):
        Thread(target=set_is_typing, args=(chat_id, tg_bot_token)).start()
        try:
            result_generate = self.gpt4_generate(prompt=prompt, chat_id=chat_id, tg_bot_token=tg_bot_token)
            if result_generate:
                STOP_TYPING = True
                logger.debug(f"Result sent successful for chat id: {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        STOP_TYPING = True  # noqa F841
        self.send_message("Smth error", chat_id, tg_bot_token)
        return False

    def gpt4_generate(self, chat_id, tg_bot_token, prompt):
        bot = telebot.TeleBot(tg_bot_token.get_secret_value())
        msg_id = bot.send_message(chat_id, 'Wait please...', parse_mode='Markdown').message_id
        response = g4f.ChatCompletion.create(
            model='gpt-4',
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            provider=g4f.Provider.Forefront
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
                    msg_id = self.send_message(
                        text=get_str_from_list(full_text[last_len_list:]),
                        chat_id=chat_id,
                        tg_bot_token=tg_bot_token
                    )
                    len_list = len(full_text)
                    cnt_divisions += 1
                else:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        text=get_str_from_list(full_text[len_list:]),
                        message_id=msg_id
                    )
                    last_len_list = len(full_text)
        bot.edit_message_text(chat_id=chat_id, text=get_str_from_list(full_text[len_list:]), message_id=msg_id)
        return True

    def send_message(self, text, chat_id, tg_bot_token):
        bot = telebot.TeleBot(tg_bot_token.get_secret_value())
        max_length = 4096
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        msg_id = 0
        for chunk in chunks:
            msg_id = bot.send_message(chat_id, chunk, parse_mode='Markdown').message_id
        return msg_id
