# Pesan Kaos Bani Zainuddin

## Purpose
Indonesian merchandise pre-order site for black/white Bani Zainuddin T-shirts. Customers do not create accounts; their phone number identifies their order history.

## Data model
- `CatalogResponse`: configuration for the built-in Bani Zainuddin shirt, including editable per-variant pricing, payment instructions, and admin-uploaded image URLs.
- `MerchandiseProduct`: name, description, image, active/draft state, and flexible purchasable variant combinations (color, model, size, price). The built-in shirt is generated from its dedicated settings; additional products are stored in Mongo `products`.
- `Order`: customer name, phone, address, payment method (`transfer`/`cod`), calculated line items and total, order number, creation time, and status.
- Pricing is stored in Mongo `settings` under `key=pricing`; orders store normalized phone digits for lookup.

## Key flows
1. Storefront: active products appear as catalog cards. Selecting a product loads its colors, models, sizes, and live price; one cart can contain multiple merchandise types.
2. Checkout: enter full name, phone, address, and transfer/COD; backend recalculates prices and saves the order; transfer instructions or COD guidance appears after success.
3. Public lookup: `/pesanan` searches order history by phone number and shows expandable summaries/statuses.
4. Admin: `/admin` requires the six-digit PIN from `backend/.env`, lists all orders, changes status, edits built-in shirt pricing, manages transfer accounts, uploads shirt images, and auto-refreshes order notifications.
5. Product management: `/admin/produk` creates merchandise with a required photo and flexible variation rows, saves it as active or draft, and allows later editing, activation/deactivation, photo replacement, or deletion. Only active products appear publicly.

## Statuses
Menunggu pembayaran, Transfer terverifikasi, Sedang diproduksi, Siap diambil, Selesai, Dibatalkan.

## Notes
Final initial prices: children Rp67.000 short / Rp77.000 long; S–XL Rp97.000 short / Rp107.000 long; XXL–4XL Rp107.000 short / Rp117.000 long. Initial transfer account is BRI 654601043399535 under Ahmad Hassan Tsabit. Admin can change every price, account, and product image from the dashboard.