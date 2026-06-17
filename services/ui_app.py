from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


# =========================
# メインダッシュボード
# =========================
@app.get("/", response_class=HTMLResponse)
def dashboard():

    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SaaS Dashboard</title>

<style>
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI";
    background: #0b0f19;
    color: #e5e7eb;
}

.sidebar {
    width: 240px;
    height: 100vh;
    position: fixed;
    background: #111827;
    padding: 20px;
}

.main {
    margin-left: 260px;
    padding: 30px;
}

.card {
    background: #111827;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
}

.title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
}

.nav a {
    display: block;
    color: #9ca3af;
    text-decoration: none;
    padding: 10px 0;
}

.nav a:hover {
    color: white;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}

.log-box {
    height: 200px;
    overflow-y: auto;
    background: #0f172a;
    padding: 10px;
    border-radius: 8px;
    font-size: 12px;
}

.notif-box {
    background: #0f172a;
    padding: 10px;
    border-radius: 8px;
    min-height: 100px;
    font-size: 13px;
}
</style>

</head>

<body>

<div class="sidebar">
    <h2>⚡ SaaS</h2>

    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/logs">Logs</a>
        <a href="/admin">Admin</a>
    </div>
</div>

<div class="main">

    <div class="title">Realtime SaaS Dashboard</div>

    <div class="grid">

        <div class="card">
            <h3>Users</h3>
            <p>Live activity</p>
        </div>

        <div class="card">
            <h3>Revenue</h3>
            <p>Stripe enabled</p>
        </div>

        <div class="card">
            <h3>Projects</h3>
            <p>Realtime sync</p>
        </div>

    </div>

    <div class="card">
        <h3>Live Events</h3>
        <div id="log" class="log-box"></div>
    </div>

    <div class="card">
        <h3>Notifications</h3>
        <div id="notifications" class="notif-box"></div>
    </div>

</div>

<script>

// =========================
// WebSocket（リアルタイムログ）
// =========================
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function(event) {

    const data = JSON.parse(event.data);

    const log = document.getElementById("log");

    const item = document.createElement("div");

    item.innerText =
        `[${data.type}] ${data.action || ""} ${data.user || ""} ${data.project_id || ""}`;

    log.prepend(item);
};


// =========================
// 通知ロード（REST API）
// =========================
async function loadNotifications() {

    try {

        const res = await fetch("/notifications?user=test");
        const data = await res.json();

        const box = document.getElementById("notifications");
        box.innerHTML = "";

        data.forEach(n => {

            const div = document.createElement("div");
            div.innerText = "🔔 " + n.message;
            box.appendChild(div);

        });

    } catch (e) {
        console.log("notification load error", e);
    }
}

loadNotifications();

</script>

</body>
</html>
"""


# =========================
# 追加API（通知取得）
# =========================
@app.get("/notifications")
def get_notifications(user: str = "test"):

    # 簡易版（本来はDB連携）
    return [
        {"message": "ログインしました"},
        {"message": "プロジェクト更新あり"},
        {"message": "チームに招待されました"}
    ]