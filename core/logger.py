import os
from datetime import datetime

LOG_FILE = "logs/app.log"


def ensure_log_dir():
    os.makedirs("logs", exist_ok=True)


def log_event(message: str, level: str = "INFO"):
    ensure_log_dir()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] [{level}] {message}\n")


def log(message: str):
    log_event(message)


class Logger:
    def __init__(self, name: str = "app"):
        self.name = name

    def info(self, message: str):
        log_event(f"[{self.name}] {message}", "INFO")

    def warning(self, message: str):
        log_event(f"[{self.name}] {message}", "WARNING")

    def error(self, message: str):
        log_event(f"[{self.name}] {message}", "ERROR")

    def debug(self, message: str):
        log_event(f"[{self.name}] {message}", "DEBUG")

    def log(self, message: str, level: str = "INFO"):
        log_event(f"[{self.name}] {message}", level)