"use client";

import { motion } from "framer-motion";
import Link from "next/link";

const TEXT_VARIANTS = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, delay: i * 0.15, ease: [0.25, 0.46, 0.45, 0.94] },
  }),
};

export default function HeroSection() {
  return (
    <section className="relative h-screen flex items-center justify-center overflow-hidden">
      {/* Ambient gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-brand-black via-[#0f0c08] to-brand-black" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_40%,rgba(201,169,110,0.06),transparent)]" />

      {/* Fine-grain texture overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E\")", backgroundSize: "200px 200px" }}
      />

      {/* Thin gold lines */}
      <div className="absolute left-[15%] top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-brand-gold/10 to-transparent" />
      <div className="absolute right-[15%] top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-brand-gold/10 to-transparent" />

      {/* Content */}
      <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
        <motion.p
          custom={0}
          initial="hidden"
          animate="visible"
          variants={TEXT_VARIANTS}
          className="text-[11px] tracking-[0.4em] text-brand-gold uppercase mb-6"
        >
          Premium Hair & Beauty · South Africa
        </motion.p>

        <motion.h1
          custom={1}
          initial="hidden"
          animate="visible"
          variants={TEXT_VARIANTS}
          className="font-serif text-6xl md:text-8xl lg:text-9xl text-brand-cream leading-none tracking-tight mb-6"
        >
          STRANDS
        </motion.h1>

        <motion.p
          custom={2}
          initial="hidden"
          animate="visible"
          variants={TEXT_VARIANTS}
          className="text-base md:text-lg text-brand-muted max-w-lg mx-auto leading-relaxed mb-10"
        >
          Exceptional hair, sourced with intention. Every order is personally fulfilled — quality over quantity, always.
        </motion.p>

        <motion.div
          custom={3}
          initial="hidden"
          animate="visible"
          variants={TEXT_VARIANTS}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            href="/products"
            className="w-full sm:w-auto px-10 py-4 bg-brand-gold text-brand-black text-sm font-semibold tracking-widest uppercase hover:bg-brand-cream transition-colors duration-300"
          >
            Shop Now
          </Link>
          <Link
            href="/#how-it-works"
            className="w-full sm:w-auto px-10 py-4 border border-brand-border text-brand-muted text-sm tracking-widest uppercase hover:border-brand-cream hover:text-brand-cream transition-all duration-300"
          >
            How It Works
          </Link>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.8, duration: 1 }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <div className="w-px h-12 bg-gradient-to-b from-brand-gold/40 to-transparent animate-pulse" />
        <span className="text-[10px] tracking-[0.3em] text-brand-muted uppercase">Scroll</span>
      </motion.div>
    </section>
  );
}
