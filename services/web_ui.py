from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()


# =========================
# ダッシュボードUI
# =========================
@app.get("/ui", response_class=HTMLResponse)
def dashboard():

    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>mcaddon SaaS Dashboard</title>

    <style>
        body {
            font-family: Arial;
            background: #0f172a;
            color: white;
            margin: 0;
        }

        .sidebar {
            width: 250px;
            height: 100vh;
            background: #111827;
            position: fixed;
            padding: 20px;
        }

        .main {
            margin-left: 270px;
            padding: 20px;
        }

        button {
            padding: 10px;
            margin: 5px 0;
            width: 100%;
            background: #2563eb;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 6px;
        }

        input {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
        }

        .card {
            background: #1f2937;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }
    </style>
</head>

<body>

<div class="sidebar">
    <h2>mcaddon SaaS</h2>

    <button onclick="loadProjects()">📁 Projects</button>
    <button onclick="showCreate()">➕ Create Project</button>
    <button onclick="loadHistory()">📜 History</button>
</div>

<div class="main">

    <h1>Dashboard</h1>

    <div id="content"></div>

</div>


<script>

let token = "";

// =========================
// Login（簡易）
/* ========================= */
function login() {

    let username = prompt("username");
    let password = prompt("password");

    fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    })
    .then(r => r.json())
    .then(data => {
        token = data.token;
        alert("ログイン成功");
    });
}


// =========================
// プロジェクト一覧
// =========================
function loadProjects() {

    fetch("/project/list", {
        headers: {"Authorization": "Bearer " + token}
    })
    .then(r => r.json())
    .then(data => {

        let html = "<h2>Projects</h2>";

        for (let id in data) {
            html += `
                <div class="card">
                    <b>${data[id].name}</b><br>
                    <button onclick="exportProject('${id}')">Export mcaddon</button>
                </div>
            `;
        }

        document.getElementById("content").innerHTML = html;
    });
}


// =========================
// プロジェクト作成
// =========================
function showCreate() {

    let name = prompt("Project name");

    fetch("/project/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({name})
    })
    .then(() => loadProjects());
}


// =========================
// エクスポート
// =========================
function exportProject(id) {

    fetch("/project/export", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({project_id: id})
    })
    .then(r => r.json())
    .then(data => {

        window.open(data.download_url, "_blank");

    });
}


// =========================
// 履歴
// =========================
function loadHistory() {

    fetch("/history", {
        headers: {"Authorization": "Bearer " + token}
    })
    .then(r => r.json())
    .then(data => {

        let html = "<h2>History</h2>";

        data.history.forEach(h => {
            html += `
                <div class="card">
                    ${h.input} → ${h.output}
                </div>
            `;
        });

        document.getElementById("content").innerHTML = html;
    });
}

</script>

</body>
</html>
"""