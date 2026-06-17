import json
import os
from datetime import datetime

DB_FILE = "data/history.json"


# =========================
# 初期化
# =========================
def init_history():

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)


# =========================
# 全履歴読み込み
# =========================
def load_history():

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 保存
# =========================
def save_history(data):

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 履歴追加
# =========================
def add_history(username: str, input_text: str, output_text: str):

    data = load_history()

    if username not in data:
        data[username] = []

    data[username].insert(0, {
        "input": input_text,
        "output": output_text,
        "time": datetime.utcnow().isoformat()
    })

    # 最大保存数制限（軽量化）
    data[username] = data[username][:50]

    save_history(data)


# =========================
# 履歴取得
# =========================
def get_history(username: str):

    data = load_history()

    return data.get(username, [])