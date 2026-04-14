"use client";

import { motion } from "framer-motion";
import { Truck, RotateCcw, ShieldCheck, Star } from "lucide-react";

const BENEFITS = [
  { icon: Truck,       title: "Free Shipping",    desc: "On all orders over R500",         color: "text-brand-teal",           bg: "bg-brand-teal/10" },
  { icon: RotateCcw,   title: "Easy Returns",     desc: "7-day hassle-free returns",       color: "text-brand-primary",         bg: "bg-brand-primary/10" },
  { icon: ShieldCheck, title: "Secure Checkout",  desc: "Stripe-powered encryption",       color: "text-brand-orange",          bg: "bg-orange-50" },
  { icon: Star,        title: "Quality Assured",  desc: "Every item personally sourced",   color: "text-purple-500",            bg: "bg-purple-50" },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-white border-y border-brand-border/60 py-10">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {BENEFITS.map((b, i) => (
            <motion.div
              key={b.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.45, delay: i * 0.1 }}
              className="flex flex-col items-center text-center gap-3 p-4"
            >
              <div className={`w-12 h-12 rounded-2xl ${b.bg} flex items-center justify-center`}>
                <b.icon size={22} strokeWidth={1.5} className={b.color} />
              </div>
              <div>
                <h3 className="font-bold text-sm text-brand-text mb-0.5">{b.title}</h3>
                <p className="text-xs text-brand-muted">{b.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
