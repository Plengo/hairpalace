"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-white border-b border-brand-border">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-5 min-h-[420px] gap-0">

          {/* Left: text + CTA */}
          <div className="lg:col-span-3 flex flex-col justify-center py-14 pr-0 lg:pr-16">
            <motion.span
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2.5 text-brand-primary text-[11px] font-black tracking-widest uppercase mb-4"
            >
              <span className="w-8 h-0.5 bg-brand-primary rounded-full" />
              New Season · Premium Hair
            </motion.span>

            <motion.h1
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.1 }}
              className="text-5xl md:text-6xl font-extrabold text-brand-text leading-[1.08] tracking-tight mb-5"
            >
              Your Hair,{" "}
              <span className="text-brand-primary">Your Story.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-brand-muted text-base leading-relaxed max-w-md mb-8"
            >
              Premium extensions, wigs &amp; hair care — sourced fresh on every order.
              No excess stock. Just quality, delivered fast across South Africa.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-wrap items-center gap-3 mb-10"
            >
              <Link
                href="/products"
                className="px-8 py-3.5 bg-brand-primary text-white text-sm font-bold tracking-wide rounded-full hover:opacity-90 transition-opacity shadow-md shadow-brand-primary/25"
              >
                Shop Now
              </Link>
              <Link
                href="/products?category=hair_extensions"
                className="px-8 py-3.5 bg-brand-bg text-brand-text text-sm font-semibold rounded-full border border-brand-border hover:border-brand-primary hover:text-brand-primary transition-all"
              >
                Extensions →
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="flex flex-wrap items-center gap-5 text-xs text-brand-muted"
            >
              {["Free shipping R500+", "3–5 day delivery", "Secure checkout"].map((t) => (
                <span key={t} className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-teal" />
                  {t}
                </span>
              ))}
            </motion.div>
          </div>

          {/* Right: coloured promo panels */}
          <div className="hidden lg:flex lg:col-span-2 items-stretch gap-3 py-8">
            {/* Tall panel */}
            <div className="flex-1 rounded-2xl overflow-hidden relative bg-gradient-to-br from-brand-primary via-[#F04E6E] to-[#C82248]">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_80%,rgba(255,255,255,0.12),transparent)]" />
              <div className="relative z-10 h-full flex flex-col justify-end p-6">
                <span className="text-white/70 text-[10px] font-black tracking-widest uppercase mb-1">Hot Pick</span>
                <p className="text-white font-extrabold text-xl leading-tight">Brazilian<br />Extensions</p>
                <Link href="/products?category=hair_extensions" className="mt-3 inline-flex items-center gap-1 text-white/80 text-xs font-semibold hover:text-white transition-colors">
                  Shop → 
                </Link>
              </div>
            </div>
            {/* Two stacked */}
            <div className="flex-1 flex flex-col gap-3">
              <div className="flex-1 rounded-2xl overflow-hidden relative bg-gradient-to-br from-brand-teal to-[#009480]">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(255,255,255,0.15),transparent)]" />
                <div className="relative z-10 h-full flex flex-col justify-end p-5">
                  <span className="text-white/70 text-[10px] font-black tracking-widest uppercase mb-1">Trending</span>
                  <p className="text-white font-extrabold text-lg leading-tight">Premium<br />Wigs</p>
                </div>
              </div>
              <div className="flex-1 rounded-2xl overflow-hidden relative bg-gradient-to-br from-brand-orange to-[#E55A0F]">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(255,255,255,0.15),transparent)]" />
                <div className="relative z-10 h-full flex flex-col justify-end p-5">
                  <span className="text-white/70 text-[10px] font-black tracking-widest uppercase mb-1">New In</span>
                  <p className="text-white font-extrabold text-lg leading-tight">Hair<br />Care</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
