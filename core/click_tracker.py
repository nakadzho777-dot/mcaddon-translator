import os
import json
from datetime import datetime

CLICK_LOG = "data/clicks.json"


def ensure_file():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(CLICK_LOG):
        with open(CLICK_LOG, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def record_click(source: str, target: str):
    ensure_file()

    with open(CLICK_LOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.append({
        "time": datetime.now().isoformat(),
        "source": source,
        "target": target,
    })

    with open(CLICK_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "status": "ok",
        "source": source,
        "target": target,
    }