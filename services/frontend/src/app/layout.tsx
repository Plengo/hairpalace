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
  title: { default: "STRANDS", template: "%s | STRANDS" },
  description: "Premium hair & beauty. Sourced on demand. Delivered with intention.",
  keywords: ["hair extensions", "wigs", "braiding hair", "hair care", "South Africa"],
  openGraph: {
    type: "website",
    locale: "en_ZA",
    siteName: "STRANDS",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className="bg-brand-black text-brand-cream font-sans antialiased">
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#141414",
              color: "#FAF0E6",
              border: "1px solid #2A2A2A",
              borderRadius: "2px",
              fontFamily: "var(--font-inter)",
              fontSize: "14px",
            },
          }}
        />
      </body>
    </html>
  );
}
