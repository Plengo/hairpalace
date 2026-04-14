"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";
import toast from "react-hot-toast";
import { useCartStore } from "@/lib/store";
import { ordersApi, type PaymentProvider } from "@/lib/api";
import { formatZAR } from "@/lib/utils";
import { Loader2, Check } from "lucide-react";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

const STRIPE_APPEARANCE = {
  theme: "night" as const,
  variables: {
    colorPrimary: "#C9A96E",
    colorBackground: "#141414",
    colorText: "#FAF0E6",
    colorDanger: "#f87171",
    fontFamily: "Inter, system-ui, sans-serif",
    borderRadius: "0px",
    fontSizeBase: "14px",
  },
};

const PROVIDERS: {
  id: PaymentProvider;
  name: string;
  tag: string;
  description: (total: number) => string;
}[] = [
  {
    id: "yoco",
    name: "Yoco",
    tag: "Card / EFT",
    description: (t) => `Pay ${formatZAR(t)} now with your card or EFT`,
  },
  {
    id: "payjustnow",
    name: "PayJustNow",
    tag: "Buy now, pay later",
    description: (t) => `3 × ${formatZAR(t / 3)} — interest-free`,
  },
  {
    id: "payflex",
    name: "Payflex",
    tag: "Buy now, pay over 6 weeks",
    description: (t) => `4 × ${formatZAR(t / 4)} over 6 weeks`,
  },
  {
    id: "happypay",
    name: "HappyPay",
    tag: "Instalments",
    description: (t) => `Pay ${formatZAR(t)} in flexible instalments`,
  },
  {
    id: "stripe",
    name: "Credit / Debit Card",
    tag: "Powered by Stripe",
    description: (t) => `Pay ${formatZAR(t)} now via Stripe`,
  },
];

// ── Stripe inner form (needs Stripe Elements context) ─────────────────────────

function StripePaymentForm({ onSuccess }: { onSuccess: () => void }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!stripe || !elements) return;

    setLoading(true);
    const { error } = await stripe.confirmPayment({
      elements,
      redirect: "if_required",
    });

    if (error) {
      toast.error(error.message ?? "Payment failed");
      setLoading(false);
    } else {
      toast.success("Payment confirmed!");
      onSuccess();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <PaymentElement />
      <button
        type="submit"
        disabled={!stripe || loading}
        className="w-full py-4 bg-brand-gold text-brand-black text-sm font-semibold tracking-widest uppercase hover:bg-brand-cream transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading && <Loader2 size={16} className="animate-spin" />}
        {loading ? "Processing..." : "Confirm & Pay"}
      </button>
    </form>
  );
}

// ── Checkout page ─────────────────────────────────────────────────────────────

export default function CheckoutPage() {
  const router = useRouter();
  const { items, total, clearCart } = useCartStore();

  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [orderId, setOrderId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<PaymentProvider>("yoco");

  const [form, setForm] = useState({
    name: "", address: "", city: "", province: "", postal_code: "",
  });

  const orderTotal = total() + 80;

  async function handlePlaceOrder(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);

    try {
      const res = await ordersApi.create({
        items: items.map((i) => ({ product_id: i.product.id, quantity: i.quantity })),
        shipping: form,
        payment_provider: selectedProvider,
      });

      const { client_secret, checkout_url, order } = res.data;
      setOrderId(order.id);

      if (checkout_url) {
        // Redirect-based providers (Yoco, PayJustNow, Payflex, HappyPay)
        window.location.href = checkout_url;
      } else if (client_secret) {
        // Stripe: show inline payment form
        setClientSecret(client_secret);
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to place order";
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  }

  function handlePaymentSuccess() {
    clearCart();
    router.push(`/orders/${orderId}`);
  }

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-32 text-center">
        <p className="font-serif text-2xl text-brand-cream mb-4">Your bag is empty</p>
        <button
          onClick={() => router.push("/products")}
          className="text-xs text-brand-gold tracking-widest uppercase underline underline-offset-4"
        >
          Continue Shopping
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-20">
      <div className="mb-12">
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Final Step</p>
        <h1 className="font-serif text-4xl text-brand-cream">Checkout</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-12">

        {/* Left: Form / Payment */}
        <div className="lg:col-span-3 space-y-8">
          {!clientSecret ? (
            <form onSubmit={handlePlaceOrder} className="space-y-8">
              {/* Shipping */}
              <div>
                <h2 className="font-serif text-xl text-brand-cream mb-4">Shipping Details</h2>
                <div className="grid grid-cols-1 gap-4">
                  {[
                    { key: "name",        label: "Full Name",      placeholder: "Jane Doe" },
                    { key: "address",     label: "Street Address", placeholder: "12 Oak Street" },
                    { key: "city",        label: "City",           placeholder: "Johannesburg" },
                    { key: "province",    label: "Province",       placeholder: "Gauteng" },
                    { key: "postal_code", label: "Postal Code",    placeholder: "2001" },
                  ].map(({ key, label, placeholder }) => (
                    <div key={key}>
                      <label className="block text-xs tracking-widest text-brand-muted uppercase mb-1.5">
                        {label}
                      </label>
                      <input
                        required
                        value={form[key as keyof typeof form]}
                        onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                        placeholder={placeholder}
                        className="w-full bg-brand-card border border-brand-border px-4 py-3 text-sm text-brand-cream placeholder:text-brand-muted/40 focus:outline-none focus:border-brand-gold transition-colors"
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Payment method */}
              <div>
                <h2 className="font-serif text-xl text-brand-cream mb-4">Payment Method</h2>
                <div className="space-y-2">
                  {PROVIDERS.map((p) => {
                    const active = selectedProvider === p.id;
                    return (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setSelectedProvider(p.id)}
                        className={`w-full flex items-center justify-between px-4 py-3.5 border text-left transition-colors ${
                          active
                            ? "border-brand-gold bg-brand-gold/5"
                            : "border-brand-border bg-brand-card hover:border-brand-gold/40"
                        }`}
                      >
                        <span className="space-y-0.5">
                          <span className="block text-sm font-medium text-brand-cream">{p.name}</span>
                          <span className="block text-[11px] text-brand-muted/70">
                            {p.description(orderTotal)}
                          </span>
                        </span>
                        <span
                          className={`ml-4 shrink-0 text-[10px] tracking-wider uppercase px-2 py-0.5 border ${
                            active
                              ? "border-brand-gold text-brand-gold"
                              : "border-brand-border text-brand-muted/60"
                          }`}
                        >
                          {p.tag}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-4 bg-brand-gold text-brand-black text-sm font-semibold tracking-widest uppercase hover:bg-brand-cream transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {submitting && <Loader2 size={16} className="animate-spin" />}
                {submitting ? "Placing order..." : "Place Order"}
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-brand-gold mb-2">
                <Check size={18} />
                <span className="text-sm tracking-widest uppercase">Order placed — complete your payment</span>
              </div>
              <h2 className="font-serif text-xl text-brand-cream">Pay with Stripe</h2>
              <Elements stripe={stripePromise} options={{ clientSecret, appearance: STRIPE_APPEARANCE }}>
                <StripePaymentForm onSuccess={handlePaymentSuccess} />
              </Elements>
            </div>
          )}
        </div>

        {/* Right: Order summary */}
        <div className="lg:col-span-2">
          <div className="bg-brand-card border border-brand-border p-6 space-y-4 sticky top-24">
            <h2 className="font-serif text-lg text-brand-cream">Order Summary</h2>
            <ul className="space-y-3 divide-y divide-brand-border/40">
              {items.map((entry) => (
                <li key={entry.product.id} className="flex justify-between pt-3 first:pt-0 text-sm">
                  <span className="text-brand-muted line-clamp-1 flex-1 mr-4">
                    {entry.product.name} × {entry.quantity}
                  </span>
                  <span className="text-brand-cream shrink-0">
                    {formatZAR(parseFloat(entry.product.price) * entry.quantity)}
                  </span>
                </li>
              ))}
            </ul>
            <div className="border-t border-brand-border/40 pt-4 space-y-2 text-sm">
              <div className="flex justify-between text-brand-muted">
                <span>Subtotal</span><span>{formatZAR(total())}</span>
              </div>
              <div className="flex justify-between text-brand-muted">
                <span>Shipping</span><span>{formatZAR(80)}</span>
              </div>
              <div className="flex justify-between font-serif text-base text-brand-cream pt-2 border-t border-brand-border/40">
                <span>Total</span><span>{formatZAR(orderTotal)}</span>
              </div>
            </div>
            <p className="text-[11px] text-brand-muted/60 leading-relaxed">
              Sourced on order. Allow 3–5 business days. You&apos;ll receive email updates at every stage.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
