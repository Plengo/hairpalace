"use client";

import Link from "next/link";
import { ShoppingBag, Menu, X } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useCartStore, useAuthStore } from "@/lib/store";

const NAV = [
  { label: "Shop",       href: "/products" },
  { label: "Extensions", href: "/products?category=hair_extensions" },
  { label: "Wigs",       href: "/products?category=wigs" },
  { label: "Hair Care",  href: "/products?category=hair_care" },
];

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const itemCount = useCartStore((s) => s.itemCount());
  const openCart  = useCartStore((s) => s.openCart);
  const { user, logout } = useAuthStore();

  return (
    <header className="fixed top-0 inset-x-0 z-50 border-b border-brand-border/40 backdrop-blur-md bg-brand-black/80">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

        {/* Logo */}
        <Link href="/" className="font-serif text-xl tracking-[0.2em] text-brand-cream hover:text-brand-gold transition-colors">
          STRANDS
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-8">
          {NAV.map((n) => (
            <Link
              key={n.label}
              href={n.href}
              className="text-sm tracking-widest text-brand-muted uppercase hover:text-brand-cream transition-colors"
            >
              {n.label}
            </Link>
          ))}
        </nav>

        {/* Right actions */}
        <div className="flex items-center gap-4">
          {user ? (
            <div className="hidden md:flex items-center gap-4 text-sm">
              {user.is_admin && (
                <Link href="/admin" className="text-brand-gold tracking-wider uppercase text-xs hover:opacity-70 transition-opacity">
                  Admin
                </Link>
              )}
              <Link href="/orders" className="text-brand-muted hover:text-brand-cream transition-colors">
                Orders
              </Link>
              <button onClick={logout} className="text-brand-muted hover:text-brand-cream transition-colors">
                Sign out
              </button>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-4 text-sm">
              <Link href="/login"    className="text-brand-muted hover:text-brand-cream transition-colors">Sign in</Link>
              <Link href="/register" className="px-4 py-1.5 border border-brand-gold text-brand-gold text-xs tracking-widest uppercase hover:bg-brand-gold hover:text-brand-black transition-all">
                Join
              </Link>
            </div>
          )}

          {/* Cart */}
          <button
            onClick={openCart}
            className="relative p-2 text-brand-muted hover:text-brand-cream transition-colors"
            aria-label="Open cart"
          >
            <ShoppingBag size={20} strokeWidth={1.5} />
            {itemCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-brand-gold text-brand-black text-[10px] font-bold rounded-full flex items-center justify-center">
                {itemCount}
              </span>
            )}
          </button>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="md:hidden p-2 text-brand-muted hover:text-brand-cream transition-colors"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden overflow-hidden border-t border-brand-border/30 bg-brand-black"
          >
            <nav className="flex flex-col px-6 py-4 gap-4">
              {NAV.map((n) => (
                <Link
                  key={n.label}
                  href={n.href}
                  onClick={() => setMobileOpen(false)}
                  className="text-sm tracking-widest text-brand-muted uppercase hover:text-brand-cream transition-colors"
                >
                  {n.label}
                </Link>
              ))}
              <div className="border-t border-brand-border/30 pt-4 flex flex-col gap-3">
                {user ? (
                  <>
                    <Link href="/orders" onClick={() => setMobileOpen(false)} className="text-sm text-brand-muted">Orders</Link>
                    {user.is_admin && <Link href="/admin" onClick={() => setMobileOpen(false)} className="text-sm text-brand-gold">Admin</Link>}
                    <button onClick={() => { logout(); setMobileOpen(false); }} className="text-left text-sm text-brand-muted">Sign out</button>
                  </>
                ) : (
                  <>
                    <Link href="/login"    onClick={() => setMobileOpen(false)} className="text-sm text-brand-muted">Sign in</Link>
                    <Link href="/register" onClick={() => setMobileOpen(false)} className="text-sm text-brand-gold">Join</Link>
                  </>
                )}
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
