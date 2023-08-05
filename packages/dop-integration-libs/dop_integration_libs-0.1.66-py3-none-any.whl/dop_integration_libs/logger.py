"""
Logger class for logging to log server
"""
import logging
import os
import requests
from typing import Any
from .environment import Environment


class Logger(object):
    """
    Logger class for logging to log server
        .log(message) - log message
        .error(message) - log error message
        .warning(message) - log warning message
        .send_log() - send log to log server
    """

    def __init__(self, session_id: str, env: Environment):
        self.session_id = session_id
        self.env = env
        self.logger = logging.getLogger(f"{session_id}")
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(f"{session_id}_log.log")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def log(self, message: Any):
        print(message)
        self.logger.info(message)

    def error(self, message: Any):
        print(message)
        self.logger.error(message)

    def warning(self, message: Any):
        print(message)
        self.logger.warning(message)

    def debug(self, message: Any):
        print(message)
        self.logger.debug(message)

    def send_log_to_server(self, log: str):
        """
        This function is used to get the environment variables
        """
        url = f"{self.env.LOG_API_BASE_URL}/logger/log/task/session/log"
        headers = {
            "Authorization": f"Bearer {self.env.LOG_API_TOKEN}"
        }
        body = {
            "task_session_id": self.session_id,
            "log_type": "CONSOLE",
            "log_data": log

        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return True
        else:
            return None

    def send_log(self):
        """
        Send log to log server
        """
        with open(f"{self.session_id}_log.log", "r") as log_file:
            lines = log_file.readlines()
            self.send_log_to_server("".join(lines))
        os.remove(f"{self.session_id}_log.log")

    @staticmethod
    def get_logger(session_id: str, env: Environment):
        return Logger(session_id, env)
