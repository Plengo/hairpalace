"use client";

import { ShoppingBag } from "lucide-react";
import { useCartStore } from "@/lib/store";
import type { Product } from "@/lib/api";
import toast from "react-hot-toast";

export default function AddToCartButton({ product }: { product: Product }) {
  const addItem = useCartStore((s) => s.addItem);
  const openCart = useCartStore((s) => s.openCart);

  function handleAdd() {
    addItem(product);
    openCart();
    toast.success("Added to bag");
  }

  return (
    <button
      onClick={handleAdd}
      className="flex items-center justify-center gap-3 w-full py-4 bg-brand-gold text-brand-black text-sm font-semibold tracking-widest uppercase hover:bg-brand-cream transition-colors duration-300"
    >
      <ShoppingBag size={16} strokeWidth={2} />
      Add to Bag
    </button>
  );
}
