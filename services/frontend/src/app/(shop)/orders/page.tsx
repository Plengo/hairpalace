"use client";

import { useEffect, useState } from "react";
import { ordersApi, type Order } from "@/lib/api";
import { formatZAR, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { Loader2, Package } from "lucide-react";
import Link from "next/link";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ordersApi.myOrders().then((r) => setOrders(r.data.items)).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-brand-gold" size={28} />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-20">
      <div className="mb-10">
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Your Account</p>
        <h1 className="font-serif text-4xl text-brand-cream">Order History</h1>
      </div>

      {orders.length === 0 ? (
        <div className="py-24 text-center space-y-4">
          <Package size={40} strokeWidth={1} className="text-brand-muted mx-auto" />
          <p className="font-serif text-2xl text-brand-cream">No orders yet</p>
          <Link href="/products" className="text-xs text-brand-gold tracking-widest uppercase underline underline-offset-4">
            Start Shopping
          </Link>
        </div>
      ) : (
        <ul className="space-y-4">
          {orders.map((order) => (
            <li key={order.id}>
              <Link
                href={`/orders/${order.id}`}
                className="block bg-brand-card border border-brand-border hover:border-brand-gold/40 transition-all duration-300 p-6"
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <p className="font-serif text-base text-brand-cream">{order.reference}</p>
                    <p className="text-xs text-brand-muted">
                      {new Date(order.created_at).toLocaleDateString("en-ZA", {
                        day: "numeric", month: "long", year: "numeric",
                      })}
                    </p>
                    <p className="text-xs text-brand-muted">{order.items.length} item{order.items.length !== 1 ? "s" : ""}</p>
                  </div>
                  <div className="text-right space-y-1">
                    <p className={cn("text-sm font-medium", ORDER_STATUS_COLORS[order.status])}>
                      {ORDER_STATUS_LABELS[order.status]}
                    </p>
                    <p className="font-serif text-lg text-brand-cream">{formatZAR(order.total)}</p>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
