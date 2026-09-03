from urllib.parse import urlencode
from uuid import uuid4

import requests
from django.conf import settings


class DodoCheckoutError(Exception):
    pass


def dodo_api_base_url():
    if settings.DODO_PAYMENTS_ENVIRONMENT == "live_mode":
        return "https://live.dodopayments.com"
    return "https://test.dodopayments.com"


def create_checkout_session(order):
    if settings.DODO_MOCK_CHECKOUT:
        query = urlencode({"order_id": order.id, "mock_payment": "1"})
        return {
            "session_id": f"mock_{uuid4().hex[:16]}",
            "checkout_url": f"{settings.FRONTEND_RETURN_URL}?{query}",
        }

    if not settings.DODO_PAYMENTS_API_KEY:
        raise DodoCheckoutError("DODO_PAYMENTS_API_KEY is required when mock checkout is disabled.")

    payload = {
        "product_cart": [{"product_id": order.product.dodo_product_id, "quantity": 1}],
        "customer": {"email": order.customer_email, "name": order.customer_name},
        "return_url": f"{settings.FRONTEND_RETURN_URL}?order_id={order.id}",
        "metadata": {"order_id": str(order.id)},
    }

    try:
        response = requests.post(
            f"{dodo_api_base_url()}/checkouts",
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.DODO_PAYMENTS_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DodoCheckoutError(f"Dodo checkout request failed: {exc}") from exc

    data = response.json()
    if not data.get("checkout_url") or not data.get("session_id"):
        raise DodoCheckoutError("Dodo response did not include a checkout URL and session id.")
    return data
