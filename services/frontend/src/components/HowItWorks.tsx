"use client";

import { motion } from "framer-motion";
import { CreditCard, Package, Truck } from "lucide-react";

const STEPS = [
  {
    icon: CreditCard,
    step: "01",
    title: "You Order",
    desc: "Browse our curated collection and place your order. Payment is secured immediately via Stripe.",
  },
  {
    icon: Package,
    step: "02",
    title: "We Source",
    desc: "We personally source every item to order — ensuring you receive only the finest quality, never pre-stored stock.",
  },
  {
    icon: Truck,
    step: "03",
    title: "We Deliver",
    desc: "Your order is prepared and dispatched within 3–5 business days. Track every step from your dashboard.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-brand-card border-y border-brand-border/40 py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-3">The STRANDS Promise</p>
          <h2 className="font-serif text-4xl text-brand-cream">How It Works</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-brand-border/40">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.15 }}
              className="bg-brand-card p-10 flex flex-col gap-6"
            >
              <div className="flex items-start justify-between">
                <div className="w-12 h-12 border border-brand-gold/30 flex items-center justify-center">
                  <step.icon size={20} strokeWidth={1} className="text-brand-gold" />
                </div>
                <span className="font-serif text-4xl text-brand-border select-none">{step.step}</span>
              </div>
              <div>
                <h3 className="font-serif text-xl text-brand-cream mb-2">{step.title}</h3>
                <p className="text-sm text-brand-muted leading-relaxed">{step.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <p className="text-center mt-10 text-xs text-brand-muted/60 max-w-xl mx-auto leading-relaxed">
          Our order-first model means no excess stock, no waste, and a more personal service. Every item leaves our hands with care.
        </p>
      </div>
    </section>
  );
}
