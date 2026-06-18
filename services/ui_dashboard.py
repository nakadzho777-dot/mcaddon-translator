import os
from flask import Flask, request, render_template_string
from core.plan_manager import get_user_plan
from core.stripe_payments import create_checkout_session
from tools.build_tool import run_full_pipeline

app = Flask(__name__)

# =========================
# UIテンプレート
# =========================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MCAddon Translator Dashboard</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f5f5f5; }
        .box { background: white; padding: 20px; border-radius: 10px; }
        input, button { padding: 10px; margin-top: 10px; width: 100%; }
        button { background: black; color: white; cursor: pointer; }
    </style>
</head>
<body>

<div class="box">
    <h1>MCAddon Translator SaaS</h1>

    <form method="POST" action="/generate">
        <input name="user" placeholder="User ID" required>
        <input name="keyword" placeholder="Keyword" required>
        <button type="submit">記事生成</button>
    </form>

    <form method="POST" action="/upgrade">
        <input name="user" placeholder="User ID" required>
        <button type="submit">Proにアップグレード</button>
    </form>

    <p>{{ message }}</p>
</div>

</body>
</html>
"""


# =========================
# ダッシュボード
# =========================
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML, message="")


# =========================
# 記事生成
# =========================
@app.route("/generate", methods=["POST"])
def generate():
    user = request.form["user"]
    keyword = request.form["keyword"]

    plan = get_user_plan(user)

    if plan == "free":
        return render_template_string(HTML, message="❌ Freeプランは制限されています")

    result = run_full_pipeline(keyword)

    return render_template_string(HTML, message=f"✅ 生成完了: {result}")


# =========================
# アップグレード
# =========================
@app.route("/upgrade", methods=["POST"])
def upgrade():
    user = request.form["user"]

    url = create_checkout_session(user, "pro")

    return f"<a href='{url}'>👉 支払いページへ</a>"


# =========================
# 起動
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)