import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from standardwebhooks.webhooks import Webhook, WebhookVerificationError

from .dodo import DodoCheckoutError, create_checkout_session
from .models import Order, Product
from .serializers import CheckoutSerializer, OrderSerializer, ProductSerializer


@api_view(["GET"])
def product_list(request):
    products = Product.objects.filter(is_active=True).order_by("id")
    return Response(ProductSerializer(products, many=True).data)


@api_view(["POST"])
def create_checkout(request):
    serializer = CheckoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        product = Product.objects.get(id=serializer.validated_data["product_id"], is_active=True)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.create(
        product=product,
        customer_name=serializer.validated_data["customer_name"],
        customer_email=serializer.validated_data["customer_email"],
    )

    try:
        checkout = create_checkout_session(order)
    except DodoCheckoutError as exc:
        order.status = Order.Status.FAILED
        order.provider_payload = {"error": str(exc)}
        order.save(update_fields=["status", "provider_payload", "updated_at"])
        return Response({"detail": str(exc), "order_id": order.id}, status=status.HTTP_502_BAD_GATEWAY)

    order.status = Order.Status.CHECKOUT_CREATED
    order.checkout_session_id = checkout["session_id"]
    order.checkout_url = checkout["checkout_url"]
    order.provider_payload = checkout
    order.save(
        update_fields=[
            "status",
            "checkout_session_id",
            "checkout_url",
            "provider_payload",
            "updated_at",
        ]
    )

    return Response(
        {"order_id": order.id, "checkout_url": order.checkout_url, "status": order.status},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def order_detail(request, order_id):
    try:
        order = Order.objects.select_related("product").get(id=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(OrderSerializer(order).data)


@csrf_exempt
@api_view(["POST"])
def dodo_webhook(request):
    raw_body = request.body
    headers = {
        "webhook-id": request.headers.get("webhook-id", ""),
        "webhook-signature": request.headers.get("webhook-signature", ""),
        "webhook-timestamp": request.headers.get("webhook-timestamp", ""),
    }

    if settings.DODO_WEBHOOK_SECRET:
        try:
            payload = Webhook(settings.DODO_WEBHOOK_SECRET).verify(raw_body, headers)
        except WebhookVerificationError:
            return HttpResponse("invalid signature", status=400)
    else:
        if not settings.DEBUG:
            return HttpResponse("webhook secret required", status=400)
        payload = json.loads(raw_body or "{}")

    order_id = find_order_id(payload)
    if not order_id:
        return HttpResponse("ignored: no order_id metadata", status=202)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("ignored: unknown order", status=202)

    order.status = status_from_webhook(payload)
    order.provider_payment_id = find_payment_id(payload)
    order.provider_payload = payload
    order.save(update_fields=["status", "provider_payment_id", "provider_payload", "updated_at"])
    return Response({"received": True, "order_id": order.id, "status": order.status})


def find_order_id(payload):
    data = payload.get("data") or payload
    metadata = data.get("metadata") or payload.get("metadata") or {}
    return metadata.get("order_id")


def find_payment_id(payload):
    data = payload.get("data") or payload
    return data.get("payment_id") or data.get("id") or payload.get("payment_id") or ""


def status_from_webhook(payload):
    data = payload.get("data") or payload
    event_name = (payload.get("type") or payload.get("event_type") or "").lower()
    payment_status = (data.get("status") or "").lower()
    signal = f"{event_name} {payment_status}"

    if "succeed" in signal or "paid" in signal or "completed" in signal:
        return Order.Status.PAID
    if "cancel" in signal:
        return Order.Status.CANCELLED
    if "fail" in signal or "declin" in signal:
        return Order.Status.FAILED
    return Order.Status.CHECKOUT_CREATED
