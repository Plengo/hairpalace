import Link from "next/link";
import { productsApi } from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import HeroSection from "@/components/HeroSection";
import HowItWorks from "@/components/HowItWorks";
import type { Product } from "@/lib/api";

async function getFeatured(): Promise<Product[]> {
  try {
    const res = await productsApi.list({ featured: true, page_size: 4 });
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

      {/* Featured Products */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <div className="flex items-end justify-between mb-12">
          <div>
            <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Curated Selection</p>
            <h2 className="font-serif text-4xl text-brand-cream">Featured Pieces</h2>
          </div>
          <Link
            href="/products"
            className="hidden md:inline-block text-xs tracking-widest text-brand-muted uppercase border-b border-brand-border pb-0.5 hover:text-brand-cream hover:border-brand-cream transition-all"
          >
            View all →
          </Link>
        </div>

        {featured.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featured.map((p, i) => (
              <ProductCard key={p.id} product={p} index={i} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 text-brand-muted text-sm">
            Collection coming soon.
          </div>
        )}

        <div className="mt-10 text-center md:hidden">
          <Link href="/products" className="text-xs tracking-widest text-brand-gold uppercase">
            View all products →
          </Link>
        </div>
      </section>

      <HowItWorks />

      {/* CTA banner */}
      <section className="border-y border-brand-border/40 py-20 text-center">
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-4">Zero compromise</p>
        <h2 className="font-serif text-5xl md:text-6xl text-brand-cream mb-6 max-w-2xl mx-auto leading-tight">
          Hair that speaks before you do.
        </h2>
        <Link
          href="/products"
          className="inline-block mt-2 px-10 py-4 bg-brand-gold text-brand-black text-sm font-semibold tracking-widest uppercase hover:bg-brand-cream transition-colors"
        >
          Shop the Collection
        </Link>
      </section>
    </>
  );
}
