from loguru import logger


class ProxyMessage:
    def check(self, message):
        logger.debug(message)
        return True
