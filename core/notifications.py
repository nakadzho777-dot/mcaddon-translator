
import requests
import smtplib
from email.mime.text import MIMEText

# =========================
# Slack通知
# =========================
def send_slack(message: str):

    webhook = os.getenv("SLACK_WEBHOOK_URL")

    if not webhook:
        return

    requests.post(webhook, json={
        "text": message
    })


# =========================
# Email通知
# =========================
def send_email(to_email: str, subject: str, body: str):

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
    server.quit()


# =========================
# アプリ内通知（DBなし簡易版）
# =========================
IN_APP_NOTIFICATIONS = []


def push_notification(user: str, message: str):

    IN_APP_NOTIFICATIONS.append({
        "user": user,
        "message": message
    })


def get_notifications(user: str):

    return [
        n for n in IN_APP_NOTIFICATIONS
        if n["user"] == user
    ]