import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Typed API calls ───────────────────────────────────────────────────────────

export const authApi = {
  register: (data: RegisterPayload) => api.post("/auth/register", data),
  login: (data: LoginPayload) => api.post<TokenResponse>("/auth/login", data),
  me: () => api.get<UserProfile>("/auth/me"),
};

export const productsApi = {
  list: (params?: ProductListParams) => api.get<ProductListResponse>("/products", { params }),
  get: (slug: string) => api.get<Product>(`/products/${slug}`),
};

export const ordersApi = {
  create: (data: CreateOrderPayload) => api.post<OrderCreatedResponse>("/orders", data),
  myOrders: (page = 1) => api.get<OrderListResponse>("/orders/me", { params: { page } }),
  getOrder: (id: number) => api.get<Order>(`/orders/me/${id}`),
};

// ── Types ─────────────────────────────────────────────────────────────────────

export type ProductCategory =
  | "hair_extensions" | "wigs" | "braiding_hair"
  | "hair_care" | "styling_tools" | "accessories";

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  category: ProductCategory;
  price: string;
  is_featured: boolean;
  lead_time_days: number;
  images: ProductImage[];
}

export interface ProductImage {
  id: number;
  url: string;
  alt_text: string | null;
  is_primary: boolean;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProductListParams {
  page?: number;
  page_size?: number;
  category?: ProductCategory;
  featured?: boolean;
}

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  phone: string | null;
  is_admin: boolean;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface CartItem {
  product_id: number;
  quantity: number;
}

export interface ShippingAddress {
  name: string;
  address: string;
  city: string;
  province: string;
  postal_code: string;
}

export interface CreateOrderPayload {
  items: CartItem[];
  shipping: ShippingAddress;
}

export type OrderStatus =
  | "pending_payment" | "paid" | "sourcing" | "processing"
  | "shipped" | "delivered" | "cancelled" | "refunded";

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: string;
}

export interface Order {
  id: number;
  reference: string;
  status: OrderStatus;
  subtotal: string;
  shipping_fee: string;
  total: string;
  shipping_name: string;
  shipping_address: string;
  shipping_city: string;
  shipping_province: string;
  shipping_postal_code: string;
  tracking_number: string | null;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrderCreatedResponse {
  order: Order;
  client_secret: string;
}

export interface OrderListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}
