from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from core.log_manager import get_logs

app = FastAPI()


@app.get("/logs", response_class=HTMLResponse)
def logs_page():

    logs = get_logs(200)

    html_logs = ""

    for log in reversed(logs):

        html_logs += f"""
        <tr>
            <td>{log['time']}</td>
            <td>{log['username']}</td>
            <td>{log['action']}</td>
            <td>{log['detail']}</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Logs</title>

    <style>
        body {{
            background: #0f172a;
            color: white;
            font-family: Arial;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            border: 1px solid #444;
            padding: 8px;
            font-size: 12px;
        }}

        th {{
            background: #1f2937;
        }}
    </style>
</head>

<body>

<h1>📊 Activity Logs</h1>

<table>
<tr>
    <th>Time</th>
    <th>User</th>
    <th>Action</th>
    <th>Detail</th>
</tr>

{html_logs}

</table>

</body>
</html>
"""