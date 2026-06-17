import stripe
import os
from core.users_db import init_users, get_user_by_token
from core.plan_manager import set_plan

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# =========================
# Checkout Session作成
# =========================
def create_checkout_session(username: str):

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "jpy",
                "product_data": {
                    "name": "mcaddon Translator PRO"
                },
                "unit_amount": 1000,  # ¥1000/月（例）
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:8000/ui?success=1",
        cancel_url="http://localhost:8000/ui?cancel=1",
        metadata={
            "username": username
        }
    )

    return session.url