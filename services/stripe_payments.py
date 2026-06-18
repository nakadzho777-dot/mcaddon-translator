import os
import requests
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from core.license_store import create_license, verify_license

router = APIRouter(prefix="/billing", tags=["billing"])

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
SITE_URL = os.getenv(
    "SITE_URL",
    "https://mcaddon-translator-production.up.railway.app"
)


@router.get("/health")
def billing_health():
    return {
        "status": "ok",
        "stripe_key": bool(STRIPE_SECRET_KEY),
        "price_id": bool(STRIPE_PRICE_ID),
    }


@router.get("/checkout")
def checkout():
    if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
        return HTMLResponse("""
<h1>Stripe設定が未完了です</h1>
<p>Railwayに STRIPE_SECRET_KEY と STRIPE_PRICE_ID を設定してください。</p>
""", status_code=500)

    res = requests.post(
        "https://api.stripe.com/v1/checkout/sessions",
        auth=(STRIPE_SECRET_KEY, ""),
        data={
            "mode": "payment",
            "line_items[0][price]": STRIPE_PRICE_ID,
            "line_items[0][quantity]": "1",
            "success_url": f"{SITE_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{SITE_URL}/pricing",
            "allow_promotion_codes": "true",
        },
        timeout=30,
    )

    if res.status_code >= 400:
        return HTMLResponse(f"""
<h1>Checkout作成エラー</h1>
<pre>{res.text}</pre>
""", status_code=500)

    data = res.json()
    return RedirectResponse(data["url"])


@router.get("/success")
def success(session_id: str = Query(default="")):
    if not session_id:
        return HTMLResponse("<h1>session_id がありません</h1>", status_code=400)

    res = requests.get(
        f"https://api.stripe.com/v1/checkout/sessions/{session_id}",
        auth=(STRIPE_SECRET_KEY, ""),
        timeout=30,
    )

    if res.status_code >= 400:
        return HTMLResponse(f"<h1>Stripe確認エラー</h1><pre>{res.text}</pre>", status_code=500)

    session = res.json()

    if session.get("payment_status") != "paid":
        return HTMLResponse("<h1>支払いが完了していません</h1>", status_code=400)

    email = (
        session.get("customer_details", {}).get("email")
        or session.get("customer_email")
        or "unknown@example.com"
    )

    license_key = create_license(email=email, source="stripe")

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Proライセンス発行完了</title>
</head>
<body>
<h1>Proライセンス発行完了</h1>

<p>支払いが確認されました。</p>

<h2>あなたのライセンスキー</h2>
<pre style="font-size:20px; padding:12px; border:1px solid #ccc;">{license_key}</pre>

<p>このキーをMCAddon Translator Pro版に入力してください。</p>
<p><a href="/">トップへ戻る</a></p>
</body>
</html>
""")


@router.get("/verify")
def verify(key: str = Query(default="")):
    return verify_license(key)