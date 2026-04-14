import Link from "next/link";
import { productsApi } from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import HeroSection from "@/components/HeroSection";
import HowItWorks from "@/components/HowItWorks";
import type { Product } from "@/lib/api";

const CATEGORIES = [
  { label: "Hair Extensions", href: "/products?category=hair_extensions", emoji: "💫", gradient: "from-rose-50 to-pink-50",   border: "hover:border-rose-200" },
  { label: "Wigs",            href: "/products?category=wigs",            emoji: "👑", gradient: "from-violet-50 to-purple-50", border: "hover:border-violet-200" },
  { label: "Braiding Hair",   href: "/products?category=braiding_hair",   emoji: "✨", gradient: "from-amber-50 to-yellow-50",  border: "hover:border-amber-200" },
  { label: "Hair Care",       href: "/products?category=hair_care",       emoji: "🌿", gradient: "from-emerald-50 to-teal-50",  border: "hover:border-emerald-200" },
];

async function getFeatured(): Promise<Product[]> {
  try {
    const res = await productsApi.list({ featured: true, page_size: 8 });
    return res.data.items;
  } catch {
    return [];
  }
}

export default async function HomePage() {
  const featured = await getFeatured();

  return (
    <>
      <HeroSection />
      <HowItWorks />

      {/* ── Shop by Category ──────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 py-14">
        <div className="flex items-end justify-between mb-7">
          <div>
            <p className="text-[11px] font-black tracking-widest text-brand-primary uppercase mb-1">Browse</p>
            <h2 className="text-2xl font-extrabold text-brand-text">Shop by Category</h2>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {CATEGORIES.map((cat) => (
            <Link
              key={cat.label}
              href={cat.href}
              className={`group bg-gradient-to-br ${cat.gradient} rounded-2xl p-6 flex flex-col items-center text-center gap-3 border border-brand-border ${cat.border} hover:shadow-md transition-all duration-300`}
            >
              <span className="text-4xl group-hover:scale-110 transition-transform duration-300 select-none">{cat.emoji}</span>
              <span className="text-sm font-bold text-brand-text group-hover:text-brand-primary transition-colors leading-snug">{cat.label}</span>
              <span className="text-xs text-brand-primary font-bold opacity-0 group-hover:opacity-100 transition-opacity">Shop →</span>
            </Link>
          ))}
        </div>
      </section>

      {/* ── Featured Products ─────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 pb-16">
        <div className="flex items-end justify-between mb-7">
          <div>
            <p className="text-[11px] font-black tracking-widest text-brand-primary uppercase mb-1">Curated for you</p>
            <h2 className="text-2xl font-extrabold text-brand-text">Featured Picks</h2>
          </div>
          <Link
            href="/products"
            className="hidden md:inline-flex items-center gap-1.5 text-sm font-bold text-brand-primary hover:opacity-80 transition-opacity"
          >
            View all →
          </Link>
        </div>

        {featured.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {featured.map((p, i) => (
              <ProductCard key={p.id} product={p} index={i} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-white rounded-2xl border border-brand-border">
            <span className="text-5xl">💇</span>
            <p className="mt-4 text-brand-muted text-sm font-medium">New collection coming soon.</p>
            <Link href="/products" className="mt-3 inline-block text-xs font-bold text-brand-primary hover:opacity-80 transition-opacity">
              Browse all products →
            </Link>
          </div>
        )}

        <div className="mt-8 text-center md:hidden">
          <Link href="/products" className="inline-flex items-center gap-1 text-sm font-bold text-brand-primary">
            View all products →
          </Link>
        </div>
      </section>

      {/* ── CTA Banner ───────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 pb-16">
        <div className="bg-brand-primary rounded-3xl overflow-hidden relative">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(255,255,255,0.12),transparent)]" />
          <div className="relative z-10 max-w-2xl mx-auto px-8 py-16 text-center">
            <p className="text-white/70 text-[11px] font-black tracking-widest uppercase mb-3">Zero Compromise</p>
            <h2 className="text-4xl md:text-5xl font-extrabold text-white leading-tight mb-6">
              Hair that speaks<br />before you do.
            </h2>
            <Link
              href="/products"
              className="inline-block px-10 py-4 bg-white text-brand-primary text-sm font-extrabold tracking-wide rounded-full hover:opacity-90 transition-opacity shadow-xl"
            >
              Shop the Collection
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
