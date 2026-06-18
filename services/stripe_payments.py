import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Stripeは本番で使う想定（未設定でも動くようにしてある）
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
except Exception:
    stripe = None


router = APIRouter(prefix="/billing", tags=["billing"])


# =========================
# リクエストモデル
# =========================
class CreateCheckoutRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str


# =========================
# ヘルスチェック
# =========================
@router.get("/health")
def billing_health():
    return {
        "status": "ok",
        "stripe_loaded": stripe is not None
    }


# =========================
# Checkoutセッション作成
# =========================
@router.post("/checkout")
def create_checkout_session(req: CreateCheckoutRequest):
    if stripe is None or not stripe.api_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe API key is not configured"
        )

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": req.price_id,
                    "quantity": 1,
                }
            ],
            success_url=req.success_url,
            cancel_url=req.cancel_url,
        )

        return {
            "checkout_url": session.url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# サブスク状態ダミー確認
# =========================
@router.get("/status")
def subscription_status():
    return {
        "plan": "free",
        "status": "inactive"
    }


# =========================
# Webhook（将来用）
# =========================
@router.post("/webhook")
def stripe_webhook():
    # 今は最小構成（後で拡張）
    return {"received": True}