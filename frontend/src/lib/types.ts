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
  child_price?: number;
  prices: Record<string, number>;
}

export interface PaymentAccount {
  id?: string;
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

export interface AdminSettings {
  pricing: Pricing;
  accounts: PaymentAccount[];
  images: Record<string, string>;
}

export interface AdminSession {
  authenticated: boolean;
}

export interface ImageUploadResponse {
  key: string;
  url: string;
  images: Record<string, string>;
}

export interface OrderItemCreate {
  product_id: string;
  variant_id?: string;
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
  product_name: string;
  color_label: string;
  sleeve_label: string;
  size_label: string;
  unit_price: number;
  line_total: number;
}

export interface MerchandiseVariant {
  id: string;
  color: string;
  model: string;
  size: string;
  price: number;
}

export interface MerchandiseProduct {
  id: string;
  name: string;
  description: string;
  image_url: string;
  active: boolean;
  editable: boolean;
  variants: MerchandiseVariant[];
  created_at: string;
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
