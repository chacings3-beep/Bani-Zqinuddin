# Pesan Kaos Bani Zainuddin

## Purpose
Indonesian merchandise pre-order site for black/white Bani Zainuddin T-shirts. Customers do not create accounts; their phone number identifies their order history.

## Data model
- `CatalogResponse`: colors (hitam/putih), sleeves (pendek/panjang), sizes (anak, S, M, L, XL, XXL, XXXL), editable pricing, payment instructions, and temporary product image URLs.
- `Order`: customer name, phone, address, payment method (`transfer`/`cod`), calculated line items and total, order number, creation time, and status.
- Pricing is stored in Mongo `settings` under `key=pricing`; orders store normalized phone digits for lookup.

## Key flows
1. Storefront: select color, sleeve, and size; price updates live; add variants to cart.
2. Checkout: enter full name, phone, address, and transfer/COD; backend recalculates prices and saves the order; transfer instructions or COD guidance appears after success.
3. Public lookup: `/pesanan` searches order history by phone number and shows expandable summaries/statuses.
4. Admin: `/admin` lists all orders, changes status, and edits starter pricing. There is no admin authentication in this MVP.

## Statuses
Menunggu pembayaran, Transfer terverifikasi, Sedang diproduksi, Siap diambil, Selesai, Dibatalkan.

## Notes
Starter prices are Rp70.000 for children, Rp85.000 for S–XL, +Rp10.000 long sleeve, +Rp5.000 XXL, and +Rp10.000 XXXL. Bank details are example values and are editable in code/catalog configuration.