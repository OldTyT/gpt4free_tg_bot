from clients.GPTGenerate import GPT4TextGenerate

from logger import logger  # noqa: F401


class FailedGenerateTextWithGPTModel(Exception):
    pass


def GenerateTextWithGPTModel(
    chat_id, prompt, tg_bot_token
) -> bool:
    gpt4 = GPT4TextGenerate()
    result = gpt4.message_responser(prompt=prompt, chat_id=chat_id, tg_bot_token=tg_bot_token)
    if result:
        return result
    # else:
    #     raise FailedGenerateTextWithGPTModel
