import logging


class Logger:
    logger: logging.Logger

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(f"logs/{name}.log", mode="w")

        formatter = logging.Formatter(
            "%(asctime)s || %(name)s || %(levelname)s || %(message)s"
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)
