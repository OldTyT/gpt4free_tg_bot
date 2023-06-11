from pydantic import BaseSettings, SecretStr
import telebot
import g4f

from logger import logger

class GPT4TextGenerate(BaseSettings):

    def message_responser(self, prompt, chat_id, tg_bot_token):
        retry = 3
        for i in range(retry):
            logger.debug(f"Retry is {i+1}/{retry} on create GPT4 text response.")
            try:
                result_generate = self.gpt4_generate(prompt=prompt)
                if result_generate:
                    self.send_message(result_generate, chat_id, tg_bot_token)
                    return True
            except:
                logger.warning("Smth error in message_responser")
            sleep(7)
        self.send_message("Smth error", chat_id, tg_bot_token)

    def gpt4_generate(self, prompt):
        return g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": prompt}], stream=False, provider=g4f.Provider.Forefront)


    def send_message(self, text, chat_id, tg_bot_token):
        bot = telebot.TeleBot(tg_bot_token.get_secret_value())
        max_length = 4096
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        for chunk in chunks:
            bot.send_message(chat_id, chunk)
        return True
