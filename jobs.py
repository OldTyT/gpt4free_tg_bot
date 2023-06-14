from clients.GPTGenerate import GPT4TextGenerate
from clients.middleware import MessagesSaver, CallbackQuerySaver

from logger import logger  # noqa: F401


class FailedGenerateTextWithGPTModel(Exception):
    pass


def GenerateTextWithGPTModel(
    chat_id, prompt, tg_bot_token, msg_id
) -> bool:
    gpt4 = GPT4TextGenerate()
    result = gpt4.message_responser(
        prompt=prompt,
        chat_id=chat_id,
        tg_bot_token=tg_bot_token,
        msg_id=msg_id
    )
    if result:
        return result
    else:
        return False
    #     raise FailedGenerateTextWithGPTModel


def SaveMessage(message):
    saver = MessagesSaver()
    result = saver.save_msg(message=message)
    if result:
        return result
    else:
        return False


def SaveCallbackQuery(callback_query):
    saver = CallbackQuerySaver()
    result = saver.save_cq(callback_query=callback_query)
    if result:
        return result
    else:
        return False
