import json
import os
from datetime import datetime

from core.logger import log_event


COST_FILE = "data/costs.json"


# =========================
# ロード
# =========================
def load_costs():
    if not os.path.exists(COST_FILE):
        return []

    try:
        with open(COST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# =========================
# 保存
# =========================
def save_costs(data):
    os.makedirs("data", exist_ok=True)

    with open(COST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# コスト記録
# =========================
def record_cost(user_id: str, action: str, cost: float):
    data = load_costs()

    data.append({
        "time": datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "cost": cost
    })

    save_costs(data)

    log_event(f"COST {user_id} {action} {cost}")


# =========================
# ユーザー別コスト
# =========================
def get_user_cost(user_id: str):
    data = load_costs()

    return sum(d["cost"] for d in data if d["user_id"] == user_id)


# =========================
# 総コスト
# =========================
def get_total_cost():
    data = load_costs()

    return sum(d["cost"] for d in data)


# =========================
# 利益計算
# =========================
def calculate_profit(revenue: float):
    cost = get_total_cost()

    return revenue - cost


# =========================
# コスト警告
# =========================
def cost_alert(threshold: float = 100.0):
    total = get_total_cost()

    if total > threshold:
        log_event(f"COST_WARNING {total}", level="WARNING")

        return {
            "status": "warning",
            "total_cost": total
        }

    return {"status": "ok"}