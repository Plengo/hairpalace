"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { ShoppingBag } from "lucide-react";
import { useCartStore } from "@/lib/store";
import { formatZAR, CATEGORY_LABELS } from "@/lib/utils";
import type { Product } from "@/lib/api";
import toast from "react-hot-toast";

interface Props {
  product: Product;
  index?: number;
}

export default function ProductCard({ product, index = 0 }: Props) {
  const addItem = useCartStore((s) => s.addItem);
  const openCart = useCartStore((s) => s.openCart);

  const primaryImage = product.images.find((i) => i.is_primary) ?? product.images[0];

  function handleAdd() {
    addItem(product);
    openCart();
    toast.success(`${product.name} added to bag`);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      className="group relative bg-brand-card border border-brand-border hover:border-brand-gold/40 transition-all duration-500"
    >
      {/* Image */}
      <Link href={`/products/${product.slug}`} className="block relative aspect-[3/4] overflow-hidden">
        {primaryImage ? (
          <Image
            src={primaryImage.url}
            alt={primaryImage.alt_text ?? product.name}
            fill
            className="object-cover transition-transform duration-700 group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="w-full h-full bg-brand-border/20 flex items-center justify-center">
            <span className="text-brand-muted text-xs">No image</span>
          </div>
        )}

        {/* Featured badge */}
        {product.is_featured && (
          <span className="absolute top-3 left-3 px-2 py-0.5 bg-brand-gold text-brand-black text-[10px] font-semibold tracking-widest uppercase">
            Featured
          </span>
        )}

        {/* Lead time */}
        <div className="absolute bottom-3 right-3 px-2 py-1 bg-brand-black/80 backdrop-blur-sm text-[10px] text-brand-muted tracking-wide">
          {product.lead_time_days}–{product.lead_time_days + 2} day delivery
        </div>
      </Link>

      {/* Info */}
      <div className="p-4 flex flex-col gap-3">
        <div>
          <p className="text-[10px] tracking-widest text-brand-gold uppercase mb-1">
            {CATEGORY_LABELS[product.category] ?? product.category}
          </p>
          <Link href={`/products/${product.slug}`}>
            <h3 className="font-serif text-base text-brand-cream group-hover:text-brand-gold transition-colors line-clamp-2">
              {product.name}
            </h3>
          </Link>
        </div>

        <div className="flex items-center justify-between mt-auto">
          <span className="font-serif text-lg text-brand-cream">
            {formatZAR(product.price)}
          </span>
          <button
            onClick={handleAdd}
            className="flex items-center gap-2 px-3 py-1.5 border border-brand-border text-brand-muted text-xs tracking-widest uppercase hover:border-brand-gold hover:text-brand-gold transition-all duration-300"
          >
            <ShoppingBag size={13} strokeWidth={1.5} />
            Add
          </button>
        </div>
      </div>
    </motion.div>
  );
}
