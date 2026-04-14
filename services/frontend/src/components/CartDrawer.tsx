"use client";

import { AnimatePresence, motion } from "framer-motion";
import { X, Trash2, ShoppingBag } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useCartStore } from "@/lib/store";
import { formatZAR } from "@/lib/utils";

export default function CartDrawer() {
  const { items, isOpen, closeCart, removeItem, updateQty, total } = useCartStore();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeCart}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
          />

          {/* Drawer */}
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-full max-w-md z-50 bg-brand-card border-l border-brand-border flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-brand-border">
              <div className="flex items-center gap-3">
                <ShoppingBag size={18} strokeWidth={1.5} className="text-brand-primary" />
                <h2 className="font-bold text-lg tracking-wide">Your Bag</h2>
              </div>
              <button onClick={closeCart} className="p-1.5 text-brand-muted hover:text-brand-text transition-colors">
                <X size={18} />
              </button>
            </div>

            {/* Items */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {items.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center gap-4 text-brand-muted">
                  <ShoppingBag size={40} strokeWidth={1} />
                  <p className="text-sm tracking-wide">Your bag is empty</p>
                  <button onClick={closeCart} className="text-xs text-brand-gold tracking-widest uppercase underline underline-offset-4">
                    Continue shopping
                  </button>
                </div>
              ) : (
                <ul className="flex flex-col gap-4">
                  {items.map((entry) => {
                    const img = entry.product.images.find((i) => i.is_primary) ?? entry.product.images[0];
                    return (
                      <li key={entry.product.id} className="flex gap-4 py-4 border-b border-brand-border/40">
                        {img && (
                          <div className="relative w-20 h-24 shrink-0 overflow-hidden bg-brand-border/20">
                            <Image src={img.url} alt={img.alt_text ?? entry.product.name} fill className="object-cover" />
                          </div>
                        )}
                        <div className="flex-1 flex flex-col justify-between">
                          <div>
                            <p className="text-sm font-semibold text-brand-text line-clamp-2">{entry.product.name}</p>
                            <p className="text-xs text-brand-muted mt-1">{formatZAR(entry.product.price)} each</p>
                          </div>
                          <div className="flex items-center justify-between">
                            {/* Qty */}
                            <div className="flex items-center border border-brand-border">
                              <button
                                onClick={() => updateQty(entry.product.id, entry.quantity - 1)}
                                className="w-7 h-7 flex items-center justify-center text-brand-muted hover:text-brand-text"
                              >−</button>
                              <span className="w-7 text-center text-sm">{entry.quantity}</span>
                              <button
                                onClick={() => updateQty(entry.product.id, entry.quantity + 1)}
                                className="w-7 h-7 flex items-center justify-center text-brand-muted hover:text-brand-text"
                              >+</button>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="text-sm font-bold text-brand-primary">
                                {formatZAR(parseFloat(entry.product.price) * entry.quantity)}
                              </span>
                              <button
                                onClick={() => removeItem(entry.product.id)}
                                className="text-brand-muted hover:text-red-400 transition-colors"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </div>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>

            {/* Footer */}
            {items.length > 0 && (
              <div className="px-6 py-6 border-t border-brand-border space-y-4">
                <div className="flex justify-between text-sm">
                  <span className="text-brand-muted tracking-wide">Subtotal</span>
                  <span className="font-bold text-brand-text">{formatZAR(total())}</span>
                </div>
                <p className="text-[11px] text-brand-muted leading-relaxed">
                  + R80 flat-rate shipping. Orders are sourced on demand — allow 3–5 business days for preparation.
                </p>
                <Link
                  href="/checkout"
                  onClick={closeCart}
                  className="block w-full py-3.5 bg-brand-primary text-white text-sm font-bold tracking-wide rounded-xl text-center hover:opacity-90 transition-opacity shadow-md shadow-brand-primary/20"
                >
                  Proceed to Checkout
                </Link>
              </div>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
