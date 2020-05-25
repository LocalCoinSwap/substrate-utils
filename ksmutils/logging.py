import logging

kusama_logger = logging.getLogger("kusama")
kusama_logger.setLevel(logging.DEBUG)


class Logger:
    def __init__(self):
        self.logger = kusama_logger

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)
