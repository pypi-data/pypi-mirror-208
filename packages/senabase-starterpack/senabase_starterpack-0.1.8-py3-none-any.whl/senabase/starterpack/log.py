import inspect
import logging
import os
from logging.handlers import RotatingFileHandler


class SimpleLogger:
    def __init__(self):
        self.log: logging.Logger = None

    def configure(self,
                  app_id: str,
                  log_level: str = "DEBUG",
                  log_fmt: str = "%(asctime)s %(levelname)s: %(message)s",
                  log_backupcount=50,
                  log_maxbytes=10000000  # 10MB
                  ) -> None:
        """
        configure logger with RotatingFileHandler
        :param app_id: application id
        :param log_level: log level (CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET)
        :param log_fmt: default %(asctime)s %(levelname)s: %(message)s
        :param log_backupcount: Backup file count (default 50)
        :param log_maxbytes: Max file size in byte for each log file (default 10000000  # 10MB)
        :return:
        """

        caller = inspect.stack()
        parent_path = os.path.dirname(caller[1].filename)

        log_file: str = f"{app_id}.log"
        log_path = os.path.join(parent_path, 'logs')
        log_file = os.path.join(log_path, log_file)

        os.makedirs(log_path, exist_ok=True)

        file_handler = RotatingFileHandler(filename=log_file, maxBytes=log_maxbytes, backupCount=log_backupcount)
        file_handler.setFormatter(logging.Formatter(log_fmt))
        stream_hander = logging.StreamHandler()
        stream_hander.setFormatter(logging.Formatter(log_fmt))
        self.log = logging.getLogger(__name__)
        self.log.addHandler(file_handler)
        self.log.addHandler(stream_hander)
        self.log.setLevel(log_level)

    def i(self, msg) -> None:
        self.log.info(msg)

    def d(self, msg) -> None:
        self.log.debug(msg)

    def e(self, ex: Exception) -> None:
        self.log.exception(ex)
