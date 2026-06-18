import stripe
import os
from fastapi import APIRouter, HTTPException
from core.db import get_conn

router = APIRouter(prefix="/billing", tags=["Billing"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PLANS = {
    "pro": 1000
}

# =========================
# Checkout
# =========================

@router.post("/checkout")
def checkout(user_id: str, plan: str):

    if plan not in PLANS:
        raise HTTPException(400, "Invalid plan")

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "jpy",
                "product_data": {"name": plan},
                "unit_amount": PLANS[plan],
            },
            "quantity": 1,
        }],
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        metadata={
            "user_id": user_id,
            "plan": plan
        }
    )

    return {"checkout_url": session.url}