from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI(title="MCAddon SaaS UI (Full Integrated)")

API_URL = "http://localhost:8000"

# =========================
# LOGIN
# =========================

@app.get("/", response_class=HTMLResponse)
def login():

    return HTMLResponse("""
    <html>
    <head>
        <title>Login</title>
        <style>
            body {
                background: #0f172a;
                color: white;
                font-family: Arial;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .box {
                background: #1f2937;
                padding: 25px;
                border-radius: 10px;
                width: 300px;
            }

            input, button {
                width: 100%;
                padding: 10px;
                margin-top: 10px;
            }

            button {
                background: #3b82f6;
                color: white;
                border: none;
                cursor: pointer;
            }
        </style>
    </head>

    <body>
        <div class="box">
            <h2>Login SaaS</h2>

            <input id="username" placeholder="username">
            <input id="password" type="password" placeholder="password">

            <button onclick="login()">Login</button>

            <p id="msg"></p>
        </div>

        <script>
            async function login() {
                const res = await fetch('""" + API_URL + """/login', {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        username: document.getElementById("username").value,
                        password: document.getElementById("password").value
                    })
                });

                const data = await res.json();

                if (data.access_token) {
                    localStorage.setItem("token", data.access_token);
                    window.location.href = "/dashboard";
                } else {
                    document.getElementById("msg").innerText = "Login failed";
                }
            }
        </script>
    </body>
    </html>
    """)

# =========================
# DASHBOARD（完全統合）
# =========================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    return HTMLResponse("""
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body {
                margin: 0;
                font-family: Arial;
                background: #0f172a;
                color: white;
                display: flex;
            }

            .sidebar {
                width: 220px;
                background: #111827;
                height: 100vh;
                padding: 20px;
            }

            .main {
                flex: 1;
                padding: 20px;
            }

            .card {
                background: #1f2937;
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
            }

            button {
                padding: 10px;
                background: #3b82f6;
                color: white;
                border: none;
                cursor: pointer;
            }
        </style>
    </head>

    <body>

        <div class="sidebar">
            <h3>SaaS Menu</h3>
            <p>Dashboard</p>
            <p>Users</p>
            <p>Projects</p>
            <p>Billing</p>
        </div>

        <div class="main">
            <h2>Dashboard</h2>

            <div class="card">
                <h3>API Status</h3>
                <p>Running ✔</p>
            </div>

            <div class="card">
                <h3>Upgrade</h3>
                <button onclick="upgrade()">Go Pro (Stripe)</button>
            </div>

            <div class="card">
                <h3>Actions</h3>
                <button onclick="loadStats()">Load Stats</button>
                <pre id="stats"></pre>
            </div>

            <button onclick="logout()">Logout</button>
        </div>

        <script>
            function getToken() {
                return localStorage.getItem("token");
            }

            function logout() {
                localStorage.removeItem("token");
                window.location.href = "/";
            }

            async function loadStats() {
                const res = await fetch('""" + API_URL + """/admin/stats');
                const data = await res.json();
                document.getElementById("stats").innerText = JSON.stringify(data, null, 2);
            }

            async function upgrade() {
                const token = getToken();

                const res = await fetch('""" + API_URL + """/billing/checkout', {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        user_id: "demo_user",
                        plan: "pro"
                    })
                });

                const data = await res.json();

                if (data.checkout_url) {
                    window.location.href = data.checkout_url;
                }
            }
        </script>

    </body>
    </html>
    """)