import type { Metadata } from "next";
import { productsApi } from "@/lib/api";
import ProductsClient from "./ProductsClient";
import type { ProductCategory } from "@/lib/api";

export const metadata: Metadata = { title: "Shop" };

interface Props {
  searchParams: Promise<{ category?: string; page?: string }>;
}

export default async function ProductsPage({ searchParams }: Props) {
  const { category, page: pageStr } = await searchParams;
  const page = pageStr ? parseInt(pageStr) : 1;

  const res = await productsApi
    .list({ page, page_size: 12, category: category as ProductCategory })
    .catch(() => null);

  return (
    <ProductsClient
      initialData={res?.data ?? { items: [], total: 0, page: 1, page_size: 12 }}
      activeCategory={(category as ProductCategory) ?? null}
    />
  );
}
