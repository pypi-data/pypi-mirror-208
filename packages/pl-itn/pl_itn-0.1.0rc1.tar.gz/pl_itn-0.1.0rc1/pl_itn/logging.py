import logging

log_level = {"info": logging.INFO, "debug": logging.DEBUG}


class ITN_logger:
    def __init__(self, logger_name: str):
        self._logger = logging.getLogger(logger_name)
        self.console_handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s] - %(message)s"
        )
        self.console_handler.setFormatter(self.formatter)
        self._logger.addHandler(self.console_handler)

    @property
    def logger(self):
        return self._logger

    def set_level(self, level: str):
        self.logger.setLevel(log_level[level])
        self.console_handler.setLevel(log_level[level])
