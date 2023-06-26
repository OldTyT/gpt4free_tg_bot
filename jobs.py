from clients.GPTGenerate import GPT4TextGenerate
from clients.middleware import MessagesSaver, CallbackQuerySaver, UpdateLastTimeMessage

from logger import logger  # noqa: F401


def GenerateTextWithGPTModel(chat_id, prompt, msg_id):
    gpt4 = GPT4TextGenerate()
    result = gpt4.message_responser(
        prompt=prompt,
        chat_id=chat_id,
        msg_id=msg_id
    )
    if result:
        return result
    else:
        raise RuntimeError


def SaveMessage(message):
    saver = MessagesSaver()
    result = saver.save_msg(message=message)
    if result:
        return result
    else:
        raise RuntimeError


def UpdateLastTime(time: int, chat_id: int):
    updater = UpdateLastTimeMessage()
    result = updater.update(time=time, chat_id=chat_id)
    if result:
        return result
    else:
        raise RuntimeError


def SaveCallbackQuery(callback_query):
    saver = CallbackQuerySaver()
    result = saver.save_cq(callback_query=callback_query)
    if result:
        return result
    else:
        raise RuntimeError
