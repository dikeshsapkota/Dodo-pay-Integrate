# Dodo Payments Mini Demo

Small React + Django demo showing the hosted checkout flow:

1. React lists a product and posts customer details to Django.
2. Django creates a local order.
3. Django calls Dodo Payments `POST /checkouts` securely with the API key.
4. React redirects the customer to Dodo's hosted checkout URL.
5. Dodo sends a signed webhook to Django.
6. Django verifies the webhook and updates the local order status.

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8000
```

Local demo mode is enabled by default and returns a fake checkout URL back to the React status page.

For real Dodo test mode, set:

```bash
export DODO_MOCK_CHECKOUT=0
export DODO_PAYMENTS_ENVIRONMENT=test_mode
export DODO_PAYMENTS_API_KEY=your_dodo_api_key
export DODO_WEBHOOK_SECRET=whsec_your_webhook_secret
export DODO_DEMO_PRODUCT_ID=your_dodo_product_id
python manage.py seed_demo
python manage.py runserver 8000
```

Webhook endpoint:

```text
POST http://localhost:8000/api/webhooks/dodo/
```

Use a tunnel such as ngrok for Dodo to reach your local backend.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Useful API Calls

Create checkout:

```bash
curl -X POST http://localhost:8000/api/checkout/ \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"customer_name":"Demo Customer","customer_email":"demo@example.com"}'
```

Unsigned local webhook test while `DJANGO_DEBUG=1` and `DODO_WEBHOOK_SECRET` is empty:

```bash
curl -X POST http://localhost:8000/api/webhooks/dodo/ \
  -H "Content-Type: application/json" \
  -d '{"type":"payment.succeeded","data":{"id":"pay_demo","status":"succeeded","metadata":{"order_id":"1"}}}'
```

When `DODO_WEBHOOK_SECRET` is set, the webhook must include valid Standard Webhooks headers:
`webhook-id`, `webhook-timestamp`, and `webhook-signature`.
