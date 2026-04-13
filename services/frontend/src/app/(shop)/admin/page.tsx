"use client";

import { useEffect, useState, useCallback } from "react";
import api, { type Order, type OrderStatus } from "@/lib/api";
import { formatZAR, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { Loader2, RefreshCw, ChevronDown } from "lucide-react";
import toast from "react-hot-toast";
import { useAuthStore } from "@/lib/store";
import { useRouter } from "next/navigation";

const STATUSES: Array<OrderStatus | "all"> = [
  "all", "paid", "sourcing", "processing", "shipped", "delivered", "cancelled",
];

interface AdminOrderListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}

export default function AdminPage() {
  const router  = useRouter();
  const { user } = useAuthStore();
  const [orders, setOrders]       = useState<Order[]>([]);
  const [loading, setLoading]     = useState(true);
  const [filter, setFilter]       = useState<OrderStatus | "all">("all");
  const [expandedId, setExpanded] = useState<number | null>(null);
  const [updating, setUpdating]   = useState<number | null>(null);

  useEffect(() => {
    if (user && !user.is_admin) router.push("/");
  }, [user, router]);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const params = filter !== "all" ? { order_status: filter } : {};
      const res = await api.get<AdminOrderListResponse>("/orders/admin", { params });
      setOrders(res.data.items);
    } catch {
      toast.error("Failed to load orders");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  async function updateStatus(orderId: number, status: OrderStatus) {
    setUpdating(orderId);
    try {
      await api.patch(`/orders/admin/${orderId}`, { status });
      toast.success("Order updated");
      fetchOrders();
    } catch {
      toast.error("Update failed");
    } finally {
      setUpdating(null);
    }
  }

  async function updateTracking(orderId: number, tracking_number: string) {
    setUpdating(orderId);
    try {
      await api.patch(`/orders/admin/${orderId}`, { tracking_number });
      toast.success("Tracking number saved");
      fetchOrders();
    } catch {
      toast.error("Failed to save tracking");
    } finally {
      setUpdating(null);
    }
  }

  return (
    <div className="min-h-screen bg-brand-black">
      <div className="max-w-7xl mx-auto px-6 py-16">

        {/* Title */}
        <div className="flex items-end justify-between mb-10">
          <div>
            <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Admin Dashboard</p>
            <h1 className="font-serif text-4xl text-brand-cream">Order Management</h1>
          </div>
          <button
            onClick={fetchOrders}
            className="flex items-center gap-2 text-xs text-brand-muted tracking-widest uppercase hover:text-brand-cream transition-colors"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>

        {/* Filter */}
        <div className="flex flex-wrap gap-2 mb-8">
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={cn(
                "px-4 py-1.5 text-xs tracking-widest uppercase border transition-all",
                filter === s
                  ? "border-brand-gold text-brand-gold bg-brand-gold/5"
                  : "border-brand-border text-brand-muted hover:border-brand-cream hover:text-brand-cream"
              )}
            >
              {s === "all" ? "All Orders" : ORDER_STATUS_LABELS[s]}
            </button>
          ))}
        </div>

        {/* Orders */}
        {loading ? (
          <div className="flex items-center justify-center h-40">
            <Loader2 className="animate-spin text-brand-gold" size={28} />
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-24 text-brand-muted">No orders found.</div>
        ) : (
          <div className="space-y-3">
            {orders.map((order) => (
              <div key={order.id} className="bg-brand-card border border-brand-border">
                {/* Row */}
                <button
                  onClick={() => setExpanded(expandedId === order.id ? null : order.id)}
                  className="w-full flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-6 py-5 text-left hover:bg-brand-border/10 transition-colors"
                >
                  <div className="flex items-center gap-6">
                    <div>
                      <p className="font-serif text-base text-brand-cream">{order.reference}</p>
                      <p className="text-xs text-brand-muted mt-0.5">
                        {new Date(order.created_at).toLocaleDateString("en-ZA")} · {order.items.length} item{order.items.length !== 1 ? "s" : ""}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <p className={cn("text-sm font-medium", ORDER_STATUS_COLORS[order.status])}>
                      {ORDER_STATUS_LABELS[order.status]}
                    </p>
                    <p className="font-serif text-base text-brand-cream">{formatZAR(order.total)}</p>
                    <ChevronDown
                      size={16}
                      className={cn(
                        "text-brand-muted transition-transform",
                        expandedId === order.id && "rotate-180"
                      )}
                    />
                  </div>
                </button>

                {/* Expanded detail */}
                {expandedId === order.id && (
                  <div className="border-t border-brand-border px-6 py-6 space-y-6">
                    {/* Items */}
                    <div>
                      <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-3">Items to Source & Ship</p>
                      <ul className="space-y-1.5">
                        {order.items.map((item) => (
                          <li key={item.id} className="flex justify-between text-sm">
                            <span className="text-brand-cream">
                              {item.product_name} <span className="text-brand-muted">× {item.quantity}</span>
                            </span>
                            <span className="text-brand-muted">{formatZAR(item.unit_price)} each</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Shipping address */}
                    <div>
                      <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Ship To</p>
                      <p className="text-sm text-brand-muted">
                        {order.shipping_name} · {order.shipping_address}, {order.shipping_city}, {order.shipping_province} {order.shipping_postal_code}
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Status update */}
                      <div>
                        <p className="text-[11px] tracking-widest text-brand-muted uppercase mb-2">Update Status</p>
                        <div className="flex flex-wrap gap-2">
                          {(["sourcing", "processing", "shipped", "delivered", "cancelled"] as OrderStatus[]).map((s) => (
                            <button
                              key={s}
                              disabled={order.status === s || updating === order.id}
                              onClick={() => updateStatus(order.id, s)}
                              className={cn(
                                "px-3 py-1.5 text-[11px] tracking-widest uppercase border transition-all disabled:opacity-40",
                                order.status === s
                                  ? "border-brand-gold text-brand-gold"
                                  : "border-brand-border text-brand-muted hover:border-brand-cream hover:text-brand-cream"
                              )}
                            >
                              {updating === order.id ? <Loader2 size={12} className="animate-spin" /> : ORDER_STATUS_LABELS[s]}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Tracking number */}
                      <div>
                        <p className="text-[11px] tracking-widest text-brand-muted uppercase mb-2">Tracking Number</p>
                        <TrackingInput
                          defaultValue={order.tracking_number ?? ""}
                          onSave={(t) => updateTracking(order.id, t)}
                          disabled={updating === order.id}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TrackingInput({
  defaultValue,
  onSave,
  disabled,
}: {
  defaultValue: string;
  onSave: (v: string) => void;
  disabled: boolean;
}) {
  const [value, setValue] = useState(defaultValue);
  return (
    <div className="flex gap-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="e.g. SASSA-12345"
        className="flex-1 bg-brand-black border border-brand-border px-3 py-2 text-sm text-brand-cream placeholder:text-brand-muted/40 focus:outline-none focus:border-brand-gold transition-colors"
      />
      <button
        onClick={() => onSave(value)}
        disabled={disabled || value === defaultValue}
        className="px-4 py-2 bg-brand-gold text-brand-black text-xs font-semibold tracking-widest uppercase hover:bg-brand-cream transition-colors disabled:opacity-40"
      >
        Save
      </button>
    </div>
  );
}
