"use client";

import { useRouter, useSearchParams } from "next/navigation";
import ProductCard from "@/components/ProductCard";
import { CATEGORY_LABELS } from "@/lib/utils";
import type { ProductCategory, ProductListResponse } from "@/lib/api";

const CATEGORIES: Array<{ key: ProductCategory | "all"; label: string }> = [
  { key: "all",             label: "All" },
  { key: "hair_extensions", label: "Hair Extensions" },
  { key: "wigs",            label: "Wigs" },
  { key: "braiding_hair",   label: "Braiding Hair" },
  { key: "hair_care",       label: "Hair Care" },
  { key: "styling_tools",   label: "Styling Tools" },
  { key: "accessories",     label: "Accessories" },
];

interface Props {
  initialData: ProductListResponse;
  activeCategory: ProductCategory | null;
}

export default function ProductsClient({ initialData, activeCategory }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function setCategory(cat: ProductCategory | "all") {
    const params = new URLSearchParams(searchParams.toString());
    if (cat === "all") {
      params.delete("category");
    } else {
      params.set("category", cat);
    }
    params.delete("page");
    router.push(`/products?${params.toString()}`);
  }

  function setPage(p: number) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(p));
    router.push(`/products?${params.toString()}`);
  }

  const totalPages = Math.ceil(initialData.total / initialData.page_size);

  return (
    <div className="max-w-7xl mx-auto px-6 py-16">
      {/* Page title */}
      <div className="mb-10">
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Our Collection</p>
        <h1 className="font-serif text-5xl text-brand-cream">
          {activeCategory ? CATEGORY_LABELS[activeCategory] : "All Products"}
        </h1>
        <p className="text-sm text-brand-muted mt-2">{initialData.total} items</p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2 mb-10 border-b border-brand-border/40 pb-6">
        {CATEGORIES.map((c) => {
          const isActive = c.key === "all" ? !activeCategory : activeCategory === c.key;
          return (
            <button
              key={c.key}
              onClick={() => setCategory(c.key)}
              className={`px-4 py-1.5 text-xs tracking-widest uppercase border transition-all ${
                isActive
                  ? "border-brand-gold text-brand-gold bg-brand-gold/5"
                  : "border-brand-border text-brand-muted hover:border-brand-cream hover:text-brand-cream"
              }`}
            >
              {c.label}
            </button>
          );
        })}
      </div>

      {/* Grid */}
      {initialData.items.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {initialData.items.map((p, i) => (
            <ProductCard key={p.id} product={p} index={i} />
          ))}
        </div>
      ) : (
        <div className="py-32 text-center text-brand-muted">
          <p className="font-serif text-2xl mb-2">Nothing here yet.</p>
          <p className="text-sm">New arrivals coming soon.</p>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-16 flex items-center justify-center gap-2">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`w-9 h-9 text-sm border transition-all ${
                p === initialData.page
                  ? "border-brand-gold text-brand-gold bg-brand-gold/5"
                  : "border-brand-border text-brand-muted hover:border-brand-cream hover:text-brand-cream"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
