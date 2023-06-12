import time
from threading import Thread

import telebot
from pydantic import BaseSettings, SecretStr

import g4f
from logger import logger


STOP_TYPING = False


def set_is_typing(chat_id, tg_bot_token):
    bot = telebot.TeleBot(tg_bot_token.get_secret_value())
    while True:
        if STOP_TYPING:
            return
        bot.send_chat_action(chat_id, action="typing")
        time.sleep(4)


class GPT4TextGenerate(BaseSettings):

    def message_responser(self, prompt, chat_id, tg_bot_token):
        Thread(target=set_is_typing, args=(chat_id,tg_bot_token)).start()
        try:
            Thread(target=set_is_typing, args=(chat_id, tg_bot_token)).start()
            result_generate = self.gpt4_generate(prompt=prompt, chat_id=chat_id, tg_bot_token=tg_bot_token)
            if result_generate:
                STOP_TYPING=True
                return True
        except:
            logger.warning("Smth error in message_responser")
        STOP_TYPING=True
        self.send_message("Smth error", chat_id, tg_bot_token)


    def gpt4_generate(self, chat_id, tg_bot_token, prompt):
        bot = telebot.TeleBot(tg_bot_token.get_secret_value())
        msg_id = bot.send_message(chat_id, 'Wait please...', parse_mode='Markdown').message_id
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": prompt}], stream=True, provider=g4f.Provider.Forefront)
        full_text = ""
        max_length = 150
        number_divisions = 1
        for i in response:
            full_text += i
            if len(full_text) / (max_length * number_divisions) > 1:
                number_divisions += 1
                bot.edit_message_text(chat_id=chat_id, text=full_text, message_id=msg_id)
        bot.edit_message_text(chat_id=chat_id, text=full_text, message_id=msg_id)
        return True


    def send_message(self, text, chat_id, tg_bot_token):
        bot = telebot.TeleBot(tg_bot_token.get_secret_value())
        max_length = 4096
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        for chunk in chunks:
            bot.send_message(chat_id, chunk, parse_mode='Markdown')
        return True
