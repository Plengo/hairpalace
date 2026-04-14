import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import { Toaster } from "react-hot-toast";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  display: "swap",
});

export const metadata: Metadata = {
  title: { default: "Hair Palace", template: "%s | Hair Palace" },
  description: "Premium hair & beauty. Sourced on demand. Delivered with intention. | hairpalace.co.za",
  keywords: ["hair extensions", "wigs", "braiding hair", "hair care", "South Africa"],
  openGraph: {
    type: "website",
    locale: "en_ZA",
    siteName: "Hair Palace",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className="bg-brand-bg text-brand-text font-sans antialiased">
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#FFFFFF",
              color: "#1A1A1A",
              border: "1px solid #E5E7EB",
              borderRadius: "10px",
              fontFamily: "var(--font-inter)",
              fontSize: "14px",
              boxShadow: "0 4px 16px rgba(0,0,0,0.10)",
            },
          }}
        />
      </body>
    </html>
  );
}
