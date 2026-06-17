import logging
import os


class Logger:

    def __init__(self, name="mcaddon"):
        os.makedirs("logs", exist_ok=True)

        logging.basicConfig(
            filename="logs/app.log",
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )

        self.logger = logging.getLogger(name)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)