import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatZAR(amount: string | number): string {
  return new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR",
    minimumFractionDigits: 2,
  }).format(typeof amount === "string" ? parseFloat(amount) : amount);
}

export const ORDER_STATUS_LABELS: Record<string, string> = {
  pending_payment: "Awaiting Payment",
  paid:            "Payment Confirmed",
  sourcing:        "Sourcing Items",
  processing:      "Preparing Shipment",
  shipped:         "Shipped",
  delivered:       "Delivered",
  cancelled:       "Cancelled",
  refunded:        "Refunded",
};

export const ORDER_STATUS_COLORS: Record<string, string> = {
  pending_payment: "text-yellow-400",
  paid:            "text-blue-400",
  sourcing:        "text-purple-400",
  processing:      "text-orange-400",
  shipped:         "text-brand-gold",
  delivered:       "text-green-400",
  cancelled:       "text-red-400",
  refunded:        "text-gray-400",
};

export const CATEGORY_LABELS: Record<string, string> = {
  hair_extensions: "Hair Extensions",
  wigs:            "Wigs",
  braiding_hair:   "Braiding Hair",
  hair_care:       "Hair Care",
  styling_tools:   "Styling Tools",
  accessories:     "Accessories",
};
