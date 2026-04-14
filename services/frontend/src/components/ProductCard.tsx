"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { ShoppingBag, Heart } from "lucide-react";
import { useCartStore } from "@/lib/store";
import { formatZAR, CATEGORY_LABELS } from "@/lib/utils";
import type { Product } from "@/lib/api";
import toast from "react-hot-toast";

interface Props {
  product: Product;
  index?: number;
}

export default function ProductCard({ product, index = 0 }: Props) {
  const addItem  = useCartStore((s) => s.addItem);
  const openCart = useCartStore((s) => s.openCart);

  const primaryImage = product.images.find((i) => i.is_primary) ?? product.images[0];

  function handleAdd() {
    addItem(product);
    openCart();
    toast.success(`Added to bag!`);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      className="group bg-white rounded-2xl overflow-hidden border border-brand-border hover:border-brand-primary/40 hover:shadow-lg transition-all duration-300"
    >
      {/* Image */}
      <Link href={`/products/${product.slug}`} className="block relative aspect-[3/4] overflow-hidden bg-brand-bg">
        {primaryImage ? (
          <Image
            src={primaryImage.url}
            alt={primaryImage.alt_text ?? product.name}
            fill
            className="object-cover transition-transform duration-500 group-hover:scale-105"
            sizes="(max-width: 640px) 50vw, (max-width: 1200px) 33vw, 25vw"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center gap-2">
            <span className="text-4xl">&#128247;</span>
            <span className="text-brand-light text-xs">No image yet</span>
          </div>
        )}

        {/* Badges */}
        <div className="absolute top-2.5 left-2.5 flex flex-col gap-1.5">
          {product.is_featured && (
            <span className="px-2.5 py-0.5 bg-brand-primary text-white text-[10px] font-black rounded-full shadow-sm">
              HOT
            </span>
          )}
          <span className="px-2.5 py-0.5 bg-brand-teal text-white text-[10px] font-black rounded-full shadow-sm">
            NEW
          </span>
        </div>

        {/* Wishlist */}
        <button className="absolute top-2.5 right-2.5 w-8 h-8 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm hover:text-brand-primary active:scale-90">
          <Heart size={14} strokeWidth={1.5} />
        </button>

        {/* Quick-add slide-up */}
        <div className="absolute inset-x-0 bottom-0 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
          <button
            onClick={(e) => { e.preventDefault(); handleAdd(); }}
            className="w-full py-3 bg-brand-primary text-white text-xs font-black tracking-widest uppercase flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
          >
            <ShoppingBag size={13} />
            Quick Add
          </button>
        </div>
      </Link>

      {/* Info */}
      <div className="p-3.5">
        <p className="text-[10px] font-black text-brand-teal uppercase tracking-widest mb-1">
          {CATEGORY_LABELS[product.category] ?? product.category}
        </p>
        <Link href={`/products/${product.slug}`}>
          <h3 className="text-sm font-semibold text-brand-text group-hover:text-brand-primary transition-colors line-clamp-2 leading-snug mb-2.5">
            {product.name}
          </h3>
        </Link>
        <div className="flex items-center justify-between">
          <span className="text-base font-extrabold text-brand-primary">
            {formatZAR(product.price)}
          </span>
          <span className="text-[10px] text-brand-light flex items-center gap-1">
            {product.lead_time_days}–{product.lead_time_days + 2}d
          </span>
        </div>
        <button
          onClick={handleAdd}
          className="mt-3 w-full py-2 rounded-xl border border-brand-border text-brand-muted text-xs font-semibold flex items-center justify-center gap-2 hover:border-brand-primary hover:text-brand-primary hover:bg-brand-primary/5 transition-all"
        >
          <ShoppingBag size={12} />
          Add to Bag
        </button>
      </div>
    </motion.div>
  );
}
