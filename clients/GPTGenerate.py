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
            result_generate = self.gpt4_generate(prompt=prompt)
            if result_generate:
                STOP_TYPING=True
                self.send_message(result_generate, chat_id, tg_bot_token)
                return True
        except:
            logger.warning("Smth error in message_responser")
        STOP_TYPING=True
        self.send_message("Smth error", chat_id, tg_bot_token)


    def gpt4_generate(self, prompt):
        return g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": prompt}], stream=False, provider=g4f.Provider.Forefront)


    def send_message(self, text, chat_id, tg_bot_token):
        bot = telebot.TeleBot(tg_bot_token.get_secret_value())
        max_length = 4096
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        for chunk in chunks:
            bot.send_message(chat_id, chunk, parse_mode='Markdown')
        return True
