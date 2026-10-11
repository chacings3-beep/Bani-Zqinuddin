import { Link, useLocation } from "react-router-dom";
import { PackagePlus, Settings } from "lucide-react";

export default function AdminProductMenu() {
  const location = useLocation();
  if (!location.pathname.startsWith("/admin")) return null;
  const onProducts = location.pathname === "/admin/produk";
  return <Link to={onProducts ? "/admin" : "/admin/produk"} className="fixed bottom-5 right-5 z-[80] inline-flex h-12 items-center gap-2 bg-zinc-950 px-5 text-sm font-bold text-white shadow-xl hover:bg-zinc-800" data-testid="admin-product-menu-link">{onProducts ? <Settings className="size-4" /> : <PackagePlus className="size-4" />}{onProducts ? "Kelola pesanan" : "Kelola produk"}</Link>;
}