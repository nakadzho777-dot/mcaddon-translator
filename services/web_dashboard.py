import os
import json
from flask import Flask, request, jsonify

from core.auth import verify_user
from core.plan_manager import get_user_plan
from core.logger import log_event
from tools.build_tool import run_full_pipeline

app = Flask(__name__)

# =========================
# ユーザー状態取得
# =========================
@app.route("/api/status", methods=["GET"])
def status():
    user = request.args.get("user")

    if not verify_user(user):
        return jsonify({"error": "unauthorized"}), 403

    plan = get_user_plan(user)

    return jsonify({
        "user": user,
        "plan": plan
    })


# =========================
# 記事生成API
# =========================
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    user = data.get("user")
    keyword = data.get("keyword")

    if not verify_user(user):
        return jsonify({"error": "unauthorized"}), 403

    plan = get_user_plan(user)

    # 制限（無料ユーザー対策）
    if plan == "free":
        log_event(f"BLOCKED free user {user}")
        return jsonify({"error": "upgrade required"}), 403

    log_event(f"API_GENERATE {user} {keyword}")

    result = run_full_pipeline(keyword)

    return jsonify({
        "status": "success",
        "result": result
    })


# =========================
# ログ閲覧
# =========================
@app.route("/api/logs", methods=["GET"])
def logs():
    user = request.args.get("user")

    if not verify_user(user):
        return jsonify({"error": "unauthorized"}), 403

    if not os.path.exists("logs/logs.json"):
        return jsonify([])

    with open("logs/logs.json", "r", encoding="utf-8") as f:
        return jsonify(json.load(f))


# =========================
# 起動
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)