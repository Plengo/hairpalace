"use client";

import Link from "next/link";
import Image from "next/image";
import { ShoppingBag, Search, User, Menu, X } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useCartStore, useAuthStore } from "@/lib/store";

const PROMO_MSGS = [
  "🚚 Free shipping on orders over R500",
  "✨ New arrivals added weekly",
  "🔒 Payments secured by Stripe",
  "💯 Quality guaranteed on every order",
];

const NAV = [
  { label: "New In",        href: "/products",                              hot: true },
  { label: "Extensions",    href: "/products?category=hair_extensions" },
  { label: "Wigs",          href: "/products?category=wigs" },
  { label: "Braiding Hair", href: "/products?category=braiding_hair" },
  { label: "Hair Care",     href: "/products?category=hair_care" },
  { label: "Featured",      href: "/products?featured=true" },
];

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const itemCount = useCartStore((s) => s.itemCount());
  const openCart  = useCartStore((s) => s.openCart);
  const { user, logout } = useAuthStore();

  return (
    <header className="fixed top-0 inset-x-0 z-50">

      {/* ── Announcement marquee ──────────────────────────────────── */}
      <div className="bg-brand-primary h-9 flex items-center overflow-hidden">
        <div className="flex animate-marquee whitespace-nowrap select-none">
          {[...Array(6)].flatMap(() => PROMO_MSGS).map((msg, i) => (
            <span key={i} className="text-white text-[11px] font-medium tracking-widest px-10">{msg}</span>
          ))}
        </div>
      </div>

      {/* ── Main header row ───────────────────────────────────────── */}
      <div className="bg-white border-b border-brand-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-4">

          {/* Logo */}
          <Link href="/" className="shrink-0">
            <Image src="/logo.png" alt="Hair Palace" width={160} height={64} className="h-16 w-auto object-contain" priority />
          </Link>

          {/* Search */}
          <div className={`flex-1 mx-auto relative transition-all duration-200 hidden sm:block ${searchFocused ? "max-w-2xl" : "max-w-xl"}`}>
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-brand-light pointer-events-none" size={15} />
            <input
              type="text"
              placeholder="Search extensions, wigs, hair care…"
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
              className="w-full pl-10 pr-4 py-2.5 rounded-full text-sm bg-brand-bg border border-brand-border focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all"
            />
          </div>

          {/* Right icons */}
          <div className="flex items-center gap-0.5 ml-auto sm:ml-0 shrink-0">

            {/* Account dropdown */}
            {user ? (
              <div className="relative group">
                <button className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-brand-muted hover:text-brand-primary transition-colors rounded-lg hover:bg-brand-bg">
                  <User size={19} strokeWidth={1.5} />
                  <span className="text-[10px] font-medium hidden sm:block">Account</span>
                </button>
                <div className="absolute right-0 top-full pt-2 hidden group-hover:block w-48 z-10">
                  <div className="bg-white border border-brand-border rounded-xl shadow-xl overflow-hidden text-sm">
                    <div className="px-4 py-2.5 border-b border-brand-border">
                      <p className="text-[11px] text-brand-muted">Signed in as</p>
                      <p className="font-semibold text-brand-text text-xs truncate">{user.email}</p>
                    </div>
                    <Link href="/orders" className="block px-4 py-2.5 hover:bg-brand-bg text-brand-text transition-colors">My Orders</Link>
                    {user.is_admin && (
                      <Link href="/admin" className="block px-4 py-2.5 hover:bg-brand-bg text-brand-primary font-semibold transition-colors">Admin Panel</Link>
                    )}
                    <hr className="border-brand-border" />
                    <button onClick={logout} className="w-full text-left px-4 py-2.5 hover:bg-brand-bg text-brand-muted transition-colors">Sign Out</button>
                  </div>
                </div>
              </div>
            ) : (
              <Link href="/login" className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-brand-muted hover:text-brand-primary transition-colors rounded-lg hover:bg-brand-bg">
                <User size={19} strokeWidth={1.5} />
                <span className="text-[10px] font-medium hidden sm:block">Sign In</span>
              </Link>
            )}

            {/* Cart */}
            <button
              onClick={openCart}
              className="relative flex flex-col items-center gap-0.5 px-3 py-1.5 text-brand-muted hover:text-brand-primary transition-colors rounded-lg hover:bg-brand-bg"
              aria-label="Open cart"
            >
              <ShoppingBag size={19} strokeWidth={1.5} />
              <span className="text-[10px] font-medium hidden sm:block">Bag</span>
              {itemCount > 0 && (
                <span className="absolute top-0.5 right-0.5 min-w-[18px] h-[18px] bg-brand-primary text-white text-[10px] font-bold rounded-full flex items-center justify-center px-1 leading-none">
                  {itemCount}
                </span>
              )}
            </button>

            {/* Mobile menu toggle */}
            <button
              className="md:hidden flex flex-col items-center gap-0.5 px-2.5 py-1.5 text-brand-muted hover:text-brand-primary transition-colors rounded-lg hover:bg-brand-bg"
              onClick={() => setMobileOpen((v) => !v)}
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>

            {/* Desktop register */}
            {!user && (
              <Link href="/register" className="hidden md:inline-flex ml-2 items-center px-5 py-2 bg-brand-primary text-white text-xs font-bold tracking-wide rounded-full hover:opacity-90 transition-opacity">
                Join Free
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* ── Category nav bar (desktop) ────────────────────────────── */}
      <div className="hidden md:block bg-white border-b border-brand-border/60">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex items-center">
            {NAV.map((cat) => (
              <Link
                key={cat.label}
                href={cat.href}
                className={`relative px-4 py-3 text-sm font-semibold tracking-wide transition-all border-b-2 -mb-px hover:text-brand-primary hover:border-brand-primary ${
                  cat.hot ? "text-brand-primary border-brand-primary" : "text-brand-muted border-transparent"
                }`}
              >
                {cat.label}
                {cat.hot && (
                  <span className="ml-1.5 inline-block bg-brand-primary text-white text-[9px] font-black px-1.5 py-0.5 rounded-full align-middle leading-none">
                    NEW
                  </span>
                )}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* ── Mobile menu ───────────────────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18 }}
            className="md:hidden bg-white border-b border-brand-border shadow-lg"
          >
            {/* Mobile search */}
            <div className="sm:hidden px-4 pt-4 pb-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-light pointer-events-none" size={14} />
                <input
                  type="text"
                  placeholder="Search…"
                  className="w-full pl-9 pr-4 py-2.5 rounded-full text-sm bg-brand-bg border border-brand-border focus:border-brand-primary focus:outline-none"
                />
              </div>
            </div>
            <nav className="max-w-7xl mx-auto px-4 py-3 flex flex-col gap-0.5">
              {NAV.map((cat) => (
                <Link
                  key={cat.label}
                  href={cat.href}
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-2.5 text-sm font-semibold text-brand-text hover:text-brand-primary hover:bg-brand-bg rounded-lg transition-colors"
                >
                  {cat.label}
                </Link>
              ))}
              <div className="border-t border-brand-border/60 mt-2 pt-2 flex flex-col gap-0.5">
                {user ? (
                  <>
                    <Link href="/orders" onClick={() => setMobileOpen(false)} className="px-3 py-2.5 text-sm text-brand-muted hover:text-brand-primary hover:bg-brand-bg rounded-lg transition-colors">My Orders</Link>
                    {user.is_admin && <Link href="/admin" onClick={() => setMobileOpen(false)} className="px-3 py-2.5 text-sm text-brand-primary font-semibold hover:bg-brand-primary/10 rounded-lg transition-colors">Admin Panel</Link>}
                    <button onClick={() => { logout(); setMobileOpen(false); }} className="text-left px-3 py-2.5 text-sm text-brand-muted hover:bg-brand-bg rounded-lg transition-colors">Sign Out</button>
                  </>
                ) : (
                  <>
                    <Link href="/login" onClick={() => setMobileOpen(false)} className="px-3 py-2.5 text-sm text-brand-muted hover:text-brand-primary hover:bg-brand-bg rounded-lg transition-colors">Sign In</Link>
                    <Link href="/register" onClick={() => setMobileOpen(false)} className="px-3 py-2.5 text-sm font-bold text-brand-primary hover:bg-brand-primary/10 rounded-lg transition-colors">Create Account →</Link>
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
