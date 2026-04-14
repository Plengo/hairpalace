import Link from "next/link";
import { Instagram, Facebook, Twitter } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-white border-t border-brand-border mt-16">
      <div className="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 md:grid-cols-4 gap-10">

        {/* Brand */}
        <div className="md:col-span-2 space-y-4">
          <p className="font-extrabold text-2xl tracking-[0.15em] text-brand-text">HAIR PALACE</p>
          <p className="text-sm text-brand-muted leading-relaxed max-w-sm">
            Premium hair sourced on demand. Every order personally fulfilled — no stockpiles, no shortcuts, just quality. · hairpalace.co.za
          </p>
          <div className="flex items-center gap-2.5 pt-1">
            {[Instagram, Facebook, Twitter].map((Icon, i) => (
              <button key={i} className="w-9 h-9 rounded-full border border-brand-border flex items-center justify-center text-brand-muted hover:border-brand-primary hover:text-brand-primary hover:bg-brand-primary/5 transition-all">
                <Icon size={15} strokeWidth={1.5} />
              </button>
            ))}
          </div>
        </div>

        {/* Shop */}
        <div className="space-y-4">
          <h4 className="text-xs font-black tracking-widest text-brand-text uppercase">Shop</h4>
          <ul className="space-y-2.5 text-sm text-brand-muted">
            {[
              { label: "Hair Extensions", href: "/products?category=hair_extensions" },
              { label: "Wigs",            href: "/products?category=wigs" },
              { label: "Braiding Hair",   href: "/products?category=braiding_hair" },
              { label: "Hair Care",       href: "/products?category=hair_care" },
            ].map((l) => (
              <li key={l.label}>
                <Link href={l.href} className="hover:text-brand-primary transition-colors">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Help */}
        <div className="space-y-4">
          <h4 className="text-xs font-black tracking-widest text-brand-text uppercase">Help</h4>
          <ul className="space-y-2.5 text-sm text-brand-muted">
            {[
              { label: "How It Works",    href: "/#how-it-works" },
              { label: "Shipping Policy", href: "/shipping" },
              { label: "Returns",         href: "/returns" },
              { label: "Privacy Policy",  href: "/privacy" },
              { label: "Terms",           href: "/terms" },
            ].map((l) => (
              <li key={l.label}>
                <Link href={l.href} className="hover:text-brand-primary transition-colors">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 pb-6 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-brand-border pt-5">
        <p className="text-xs text-brand-light">
          &copy; {new Date().getFullYear()} HAIR PALACE. All rights reserved. &middot; South Africa
        </p>
        <p className="text-xs text-brand-light/70">Payments secured by Stripe &middot; Data encrypted at rest</p>
      </div>
    </footer>
  );
}
