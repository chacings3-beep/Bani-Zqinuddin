"""Customer can complete checkout for an added product without login and later find the order
by phone via /orders/lookup (criterion: checkout + phone lookup)."""

import uuid

ADMIN_PIN = "492345"


def _login(client):
    resp = client.post("/admin/login", json={"pin": ADMIN_PIN})
    assert resp.status_code == 200


def _create_active_product(client):
    files = {"file": ("tscheck-photo.png", b"\x89PNG\r\n\x1a\n fake-bytes", "image/png")}
    data = {
        "name": "tscheck-checkout-product",
        "description": "Product for checkout lookup test",
        "active": "true",
        "variants_json": '[{"id": "variant-1", "color": "Hitam", "model": "Standar", "size": "All Size", "price": 42000}]',
    }
    resp = client.post("/admin/products", data=data, files=files)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_checkout_then_lookup_by_phone(client):
    _login(client)
    product = _create_active_product(client)
    variant = product["variants"][0]

    phone = f"0813{uuid.uuid4().int % 10**8:08d}"
    order_payload = {
        "full_name": "Tscheck Pelanggan",
        "phone": phone,
        "address": "Jl. Tscheck No. 1",
        "payment_method": "cod",
        "items": [
            {
                "product_id": product["id"],
                "variant_id": variant["id"],
                "color": variant["color"],
                "sleeve": variant["model"],
                "size": variant["size"],
                "quantity": 2,
            }
        ],
    }
    order_resp = client.post("/orders", json=order_payload)
    assert order_resp.status_code == 200, f"checkout failed: {order_resp.status_code} {order_resp.text}"
    order = order_resp.json()
    assert order["order_number"]
    assert order["total_amount"] == variant["price"] * 2
    assert order["status"] == "pending"

    lookup_resp = client.get("/orders/lookup", params={"phone": phone})
    assert lookup_resp.status_code == 200, f"lookup failed: {lookup_resp.status_code} {lookup_resp.text}"
    found = lookup_resp.json()
    assert any(o["id"] == order["id"] for o in found), "order not found via phone lookup"
    matched = next(o for o in found if o["id"] == order["id"])
    assert matched["items"][0]["product_name"] == product["name"]

    # cleanup: deactivate/delete the test product so it doesn't linger in the public catalog
    client.delete(f"/admin/products/{product['id']}")
