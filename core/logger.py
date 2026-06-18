import os
from datetime import datetime

LOG_FILE = "logs/app.log"

def log_event(message: str, level: str = "INFO"):
    os.makedirs("logs", exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] [{level}] {message}\n")

def log(message: str):
    log_event(message)