export type PaymentMethodId = "transfer" | "cod";
export type OrderStatus =
  | "pending"
  | "transfer_verified"
  | "in_production"
  | "ready_for_pickup"
  | "completed"
  | "cancelled";

export interface ProductColor {
  id: string;
  label: string;
  hex: string;
}

export interface ProductSleeve {
  id: string;
  label: string;
  extra_price: number;
}

export interface ProductSize {
  id: string;
  label: string;
  category: string;
  extra_price: number;
}

export interface Pricing {
  base_price: number;
  child_price: number;
  long_sleeve_extra: number;
  xxl_extra: number;
  xxxl_extra: number;
}

export interface PaymentAccount {
  bank: string;
  account_number: string;
  account_name: string;
}

export interface PaymentMethod {
  id: PaymentMethodId;
  title: string;
  badge: string;
  description?: string;
  accounts: PaymentAccount[];
}

export interface CatalogResponse {
  product_name: string;
  colors: ProductColor[];
  sleeves: ProductSleeve[];
  sizes: ProductSize[];
  pricing: Pricing;
  payment_methods: PaymentMethod[];
  images: Record<string, string>;
}

export interface OrderItemCreate {
  color: string;
  sleeve: string;
  size: string;
  quantity: number;
}

export interface OrderCreate {
  full_name: string;
  phone: string;
  address: string;
  payment_method: PaymentMethodId;
  items: OrderItemCreate[];
}

export interface OrderItem extends OrderItemCreate {
  color_label: string;
  sleeve_label: string;
  size_label: string;
  unit_price: number;
  line_total: number;
}

export interface Order {
  id: string;
  order_number: string;
  full_name: string;
  phone: string;
  address: string;
  payment_method: PaymentMethodId;
  items: OrderItem[];
  total_amount: number;
  status: OrderStatus;
  created_at: string;
}
