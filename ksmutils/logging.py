import logging


class Logger:
    def __init__(self):
        kusama_logger = logging.getLogger("kusama")
        kusama_logger.setLevel(logging.DEBUG)
        self.logger = kusama_logger

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)


class PyTestLogger:
    """
    Used for verifying logs output in tests
    """

    def __init__(self):
        self.LAST_MESSAGE = None

    def info(self, message):
        self.LAST_MESSAGE = message

    def error(self, message):
        self.LAST_MESSAGE = message

    def debug(self, message):
        self.LAST_MESSAGE = message
