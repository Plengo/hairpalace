import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Product } from "@/lib/api";

export interface CartEntry {
  product: Product;
  quantity: number;
}

interface CartStore {
  items: CartEntry[];
  isOpen: boolean;
  addItem: (product: Product, qty?: number) => void;
  removeItem: (productId: number) => void;
  updateQty: (productId: number, qty: number) => void;
  clearCart: () => void;
  openCart: () => void;
  closeCart: () => void;
  total: () => number;
  itemCount: () => number;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      isOpen: false,

      addItem: (product, qty = 1) =>
        set((state) => {
          const existing = state.items.find((i) => i.product.id === product.id);
          if (existing) {
            return {
              items: state.items.map((i) =>
                i.product.id === product.id
                  ? { ...i, quantity: i.quantity + qty }
                  : i
              ),
            };
          }
          return { items: [...state.items, { product, quantity: qty }] };
        }),

      removeItem: (productId) =>
        set((state) => ({ items: state.items.filter((i) => i.product.id !== productId) })),

      updateQty: (productId, qty) =>
        set((state) => ({
          items:
            qty <= 0
              ? state.items.filter((i) => i.product.id !== productId)
              : state.items.map((i) =>
                  i.product.id === productId ? { ...i, quantity: qty } : i
                ),
        })),

      clearCart: () => set({ items: [] }),
      openCart: () => set({ isOpen: true }),
      closeCart: () => set({ isOpen: false }),

      total: () =>
        get().items.reduce(
          (sum, i) => sum + parseFloat(i.product.price) * i.quantity,
          0
        ),

      itemCount: () =>
        get().items.reduce((sum, i) => sum + i.quantity, 0),
    }),
    { name: "strands-cart", partialize: (s) => ({ items: s.items }) }
  )
);

// ── Auth store ────────────────────────────────────────────────────────────────

interface AuthStore {
  token: string | null;
  user: import("@/lib/api").UserProfile | null;
  setAuth: (token: string, user: import("@/lib/api").UserProfile) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token, user) => {
        localStorage.setItem("access_token", token);
        set({ token, user });
      },
      logout: () => {
        localStorage.removeItem("access_token");
        set({ token: null, user: null });
      },
    }),
    { name: "strands-auth", partialize: (s) => ({ token: s.token, user: s.user }) }
  )
);
