"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ordersApi, type Order } from "@/lib/api";
import { formatZAR, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { CheckCircle, Loader2 } from "lucide-react";

const STATUS_STEPS = [
  "pending_payment", "paid", "sourcing", "processing", "shipped", "delivered",
] as const;

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ordersApi.getOrder(parseInt(id))
      .then((r) => setOrder(r.data))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="animate-spin text-brand-gold" size={28} /></div>;
  if (!order)  return <div className="text-center py-32 text-brand-muted">Order not found.</div>;

  const currentStep = STATUS_STEPS.indexOf(order.status as typeof STATUS_STEPS[number]);

  return (
    <div className="max-w-3xl mx-auto px-6 py-20 space-y-12">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          {order.status === "delivered" && <CheckCircle size={20} className="text-green-400" />}
          <p className="text-[11px] tracking-widest text-brand-gold uppercase">Order Details</p>
        </div>
        <h1 className="font-serif text-4xl text-brand-cream">{order.reference}</h1>
        <p className={cn("text-sm mt-2 font-medium", ORDER_STATUS_COLORS[order.status])}>
          {ORDER_STATUS_LABELS[order.status]}
        </p>
      </div>

      {/* Progress tracker */}
      {!["cancelled", "refunded"].includes(order.status) && (
        <div className="flex items-center gap-0">
          {STATUS_STEPS.map((step, i) => {
            const done = i <= currentStep;
            const last = i === STATUS_STEPS.length - 1;
            return (
              <div key={step} className="flex items-center flex-1 last:flex-none">
                <div className={cn(
                  "w-3 h-3 rounded-full border flex-shrink-0 transition-all",
                  done ? "bg-brand-gold border-brand-gold" : "bg-transparent border-brand-border"
                )} />
                {!last && (
                  <div className={cn("flex-1 h-px transition-all", done && i < currentStep ? "bg-brand-gold" : "bg-brand-border")} />
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Items */}
      <div className="bg-brand-card border border-brand-border">
        <div className="px-6 py-4 border-b border-brand-border">
          <h2 className="font-serif text-lg text-brand-cream">Items</h2>
        </div>
        <ul className="divide-y divide-brand-border/40">
          {order.items.map((item) => (
            <li key={item.id} className="flex justify-between px-6 py-4 text-sm">
              <span className="text-brand-muted">{item.product_name} × {item.quantity}</span>
              <span className="text-brand-cream">{formatZAR(parseFloat(item.unit_price) * item.quantity)}</span>
            </li>
          ))}
          <li className="flex justify-between px-6 py-4 text-sm text-brand-muted">
            <span>Shipping</span>
            <span>{formatZAR(order.shipping_fee)}</span>
          </li>
          <li className="flex justify-between px-6 py-4 font-serif text-base border-t border-brand-border">
            <span className="text-brand-cream">Total</span>
            <span className="text-brand-gold">{formatZAR(order.total)}</span>
          </li>
        </ul>
      </div>

      {/* Shipping address */}
      <div className="bg-brand-card border border-brand-border p-6 space-y-2">
        <h2 className="font-serif text-lg text-brand-cream mb-3">Shipping Address</h2>
        <p className="text-sm text-brand-muted">{order.shipping_name}</p>
        <p className="text-sm text-brand-muted">{order.shipping_address}</p>
        <p className="text-sm text-brand-muted">{order.shipping_city}, {order.shipping_province} {order.shipping_postal_code}</p>
        {order.tracking_number && (
          <p className="text-sm text-brand-gold mt-3">Tracking: {order.tracking_number}</p>
        )}
      </div>
    </div>
  );
}
