import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { CheckCircle2, CreditCard, Loader2, RefreshCcw, XCircle } from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

function App() {
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState("");
  const [customerName, setCustomerName] = useState("Demo Customer");
  const [customerEmail, setCustomerEmail] = useState("demo@example.com");
  const [order, setOrder] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const params = useMemo(() => new URLSearchParams(window.location.search), []);
  const returnedOrderId = params.get("order_id");
  const mockPayment = params.get("mock_payment");

  useEffect(() => {
    fetch(`${API_BASE}/products/`)
      .then((response) => response.json())
      .then((data) => {
        setProducts(data);
        setSelectedProductId(data[0]?.id || "");
      })
      .catch(() => setMessage("Backend is not reachable yet."));
  }, []);

  useEffect(() => {
    if (returnedOrderId) {
      refreshOrder(returnedOrderId);
      setMessage(
        mockPayment
          ? "Mock checkout returned. Send a webhook to mark the order paid or failed."
          : "Returned from Dodo checkout. Waiting for webhook confirmation."
      );
    }
  }, [returnedOrderId, mockPayment]);

  async function startCheckout(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_BASE}/checkout/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: Number(selectedProductId),
          customer_name: customerName,
          customer_email: customerEmail,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Checkout failed.");
      }
      window.location.href = data.checkout_url;
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshOrder(id = order?.id || returnedOrderId) {
    if (!id) return;
    const response = await fetch(`${API_BASE}/orders/${id}/`);
    const data = await response.json();
    setOrder(data);
  }

  const selectedProduct = products.find((product) => product.id === Number(selectedProductId));

  return (
    <main className="shell">
      <section className="panel">
        <div className="intro">
          <p className="eyebrow">Dodo Payments hosted checkout</p>
          <h1>One product. One order. One webhook status.</h1>
        </div>

        <form onSubmit={startCheckout} className="checkout-form">
          <label>
            Product
            <select value={selectedProductId} onChange={(event) => setSelectedProductId(event.target.value)}>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name} - {product.price_display}
                </option>
              ))}
            </select>
          </label>

          <label>
            Name
            <input value={customerName} onChange={(event) => setCustomerName(event.target.value)} required />
          </label>

          <label>
            Email
            <input
              type="email"
              value={customerEmail}
              onChange={(event) => setCustomerEmail(event.target.value)}
              required
            />
          </label>

          <button disabled={loading || !selectedProductId}>
            {loading ? <Loader2 className="spin" size={18} /> : <CreditCard size={18} />}
            Pay with Dodo
          </button>
        </form>

        {selectedProduct && (
          <div className="product-line">
            <strong>{selectedProduct.price_display}</strong>
            <span>{selectedProduct.description}</span>
          </div>
        )}

        {message && <p className="message">{message}</p>}
      </section>

      <section className="status">
        <div>
          <p className="eyebrow">Local order record</p>
          <h2>{order ? `Order #${order.id}` : "No order selected"}</h2>
        </div>

        <StatusBadge status={order?.status} />

        {order && (
          <dl>
            <div>
              <dt>Product</dt>
              <dd>{order.product.name}</dd>
            </div>
            <div>
              <dt>Customer</dt>
              <dd>{order.customer_email}</dd>
            </div>
            <div>
              <dt>Checkout session</dt>
              <dd>{order.checkout_session_id || "Pending"}</dd>
            </div>
          </dl>
        )}

        <button className="secondary" onClick={() => refreshOrder()} disabled={!order && !returnedOrderId}>
          <RefreshCcw size={17} />
          Refresh status
        </button>
      </section>
    </main>
  );
}

function StatusBadge({ status }) {
  if (status === "paid") {
    return (
      <span className="badge paid">
        <CheckCircle2 size={18} />
        Paid
      </span>
    );
  }

  if (status === "failed" || status === "cancelled") {
    return (
      <span className="badge failed">
        <XCircle size={18} />
        {status}
      </span>
    );
  }

  return <span className="badge">{status || "Waiting"}</span>;
}

createRoot(document.getElementById("root")).render(<App />);
