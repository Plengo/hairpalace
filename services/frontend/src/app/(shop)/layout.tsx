import Header from "@/components/Header";
import Footer from "@/components/Footer";
import CartDrawer from "@/components/CartDrawer";

export default function ShopLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <CartDrawer />
      <main className="pt-36 min-h-screen bg-brand-bg">{children}</main>
      <Footer />
    </>
  );
}
