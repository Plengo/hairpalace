import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-brand-border/40 bg-brand-black mt-24">
      <div className="max-w-7xl mx-auto px-6 py-16 grid grid-cols-1 md:grid-cols-4 gap-10">

        {/* Brand */}
        <div className="md:col-span-2 space-y-4">
          <p className="font-serif text-2xl tracking-[0.2em] text-brand-cream">STRANDS</p>
          <p className="text-sm text-brand-muted leading-relaxed max-w-sm">
            Premium hair & beauty, sourced on demand. Every order is personally fulfilled — no excess stock, no compromise on quality.
          </p>
          <p className="text-xs text-brand-muted/60 tracking-wider">
            Registered Business · South Africa
          </p>
        </div>

        {/* Shop */}
        <div className="space-y-4">
          <h4 className="text-[11px] tracking-widest text-brand-gold uppercase">Shop</h4>
          <ul className="space-y-2 text-sm text-brand-muted">
            {[
              { label: "Hair Extensions", href: "/products?category=hair_extensions" },
              { label: "Wigs",            href: "/products?category=wigs" },
              { label: "Braiding Hair",   href: "/products?category=braiding_hair" },
              { label: "Hair Care",       href: "/products?category=hair_care" },
            ].map((l) => (
              <li key={l.label}>
                <Link href={l.href} className="hover:text-brand-cream transition-colors">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Info */}
        <div className="space-y-4">
          <h4 className="text-[11px] tracking-widest text-brand-gold uppercase">Info</h4>
          <ul className="space-y-2 text-sm text-brand-muted">
            {[
              { label: "How It Works",   href: "/#how-it-works" },
              { label: "Shipping Policy", href: "/shipping" },
              { label: "Returns",        href: "/returns" },
              { label: "Privacy Policy", href: "/privacy" },
              { label: "Terms of Service", href: "/terms" },
            ].map((l) => (
              <li key={l.label}>
                <Link href={l.href} className="hover:text-brand-cream transition-colors">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 pb-8 flex flex-col md:flex-row items-center justify-between gap-4 border-t border-brand-border/20 pt-6">
        <p className="text-xs text-brand-muted/50">
          © {new Date().getFullYear()} STRANDS. All rights reserved.
        </p>
        <p className="text-xs text-brand-muted/40">
          Payments secured by Stripe · Data encrypted at rest
        </p>
      </div>
    </footer>
  );
}
