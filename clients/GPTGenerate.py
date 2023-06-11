import gpt4free
from gpt4free import Provider
from pydantic import BaseSettings, SecretStr
import telebot

from logger import logger

class GPT4TextGenerate(BaseSettings):

    def message_responser(self, prompt, chat_id, tg_bot_token):
        retry = 3
        for i in range(retry):
            logger.debug(f"Retry is {i+1}/{retry} on create GPT4 text response.")
            result_generate = self.gpt4_generate(prompt=prompt)
            if result_generate:
                try:
                    self.send_message(result_generate, chat_id, tg_bot_token)
                    return True
                except:
                    pass
            sleep(30)
        self.send_message("Smth error", chat_id, tg_bot_token)
    
    def gpt4_generate(self, prompt):
        text = gpt4free.Completion.create(Provider.You, prompt=prompt)
        return text.encode().decode('unicode_escape')


    def send_message(self, text, chat_id, tg_bot_token):
        bot = telebot.TeleBot(tg_bot_token.get_secret_value())
        return bot.send_message(chat_id, text)
