import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Image from "next/image";
import { productsApi } from "@/lib/api";
import AddToCartButton from "./AddToCartButton";
import { formatZAR, CATEGORY_LABELS } from "@/lib/utils";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const res = await productsApi.get(slug).catch(() => null);
  return { title: res?.data.name ?? "Product" };
}

export default async function ProductDetailPage({ params }: Props) {
  const { slug } = await params;
  const res = await productsApi.get(slug).catch(() => null);
  if (!res) notFound();

  const product = res.data;
  const primary = product.images.find((i) => i.is_primary) ?? product.images[0];

  return (
    <div className="max-w-7xl mx-auto px-6 py-20">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">

        {/* Images */}
        <div className="space-y-4">
          <div className="relative aspect-[4/5] overflow-hidden bg-brand-card border border-brand-border">
            {primary ? (
              <Image
                src={primary.url}
                alt={primary.alt_text ?? product.name}
                fill
                className="object-cover"
                priority
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-brand-muted text-sm">No image</div>
            )}
          </div>
          {product.images.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {product.images.map((img) => (
                <div key={img.id} className="relative aspect-square overflow-hidden bg-brand-card border border-brand-border">
                  <Image src={img.url} alt={img.alt_text ?? ""} fill className="object-cover" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex flex-col gap-6 lg:py-4">
          <div>
            <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-3">
              {CATEGORY_LABELS[product.category] ?? product.category}
            </p>
            <h1 className="font-serif text-4xl md:text-5xl text-brand-cream leading-tight">
              {product.name}
            </h1>
          </div>

          <p className="font-serif text-3xl text-brand-cream">{formatZAR(product.price)}</p>

          {product.description && (
            <p className="text-sm text-brand-muted leading-relaxed">{product.description}</p>
          )}

          {/* Lead time notice */}
          <div className="border border-brand-border/60 bg-brand-card p-4 space-y-1">
            <p className="text-xs text-brand-gold tracking-wider uppercase">Order-first sourcing</p>
            <p className="text-sm text-brand-muted leading-relaxed">
              This item is sourced personally on order. Allow{" "}
              <span className="text-brand-cream">{product.lead_time_days}–{product.lead_time_days + 2} business days</span>{" "}
              for preparation before dispatch. You'll be notified at every stage.
            </p>
          </div>

          <AddToCartButton product={product} />

          {/* Assurances */}
          <ul className="space-y-2 mt-2">
            {[
              "Secure payment via Stripe",
              "Flat-rate R80 shipping nationwide",
              "Full refund if sourcing fails",
            ].map((item) => (
              <li key={item} className="flex items-center gap-2 text-xs text-brand-muted">
                <span className="w-1 h-1 rounded-full bg-brand-gold shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
