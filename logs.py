import logging
import os
from logging.handlers import RotatingFileHandler
from utils import resource_path

class Logger:

    def __init__(self, log_file=resource_path("LOG_INFO.log"), max_bytes=2097152, backup_count=5):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Create a rotating file handler and set the level to DEBUG
        file_handler = RotatingFileHandler(self.log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create a console handler and set the level to INFOs
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_variable(self, var, out):
        message = f"{var}: {out}"
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_debug(self, message):
        self.logger.debug(message)

