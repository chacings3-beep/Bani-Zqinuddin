"""Admin can add flexible merchandise products, edit/activate/deactivate/delete them, and the
built-in shirt product cannot be deleted."""

import httpx

ADMIN_PIN = "492345"


def _login(client):
    resp = client.post("/admin/login", json={"pin": ADMIN_PIN})
    assert resp.status_code == 200


def _create_product(client, name, active=True):
    files = {"file": ("tscheck-photo.png", b"\x89PNG\r\n\x1a\n fake-bytes", "image/png")}
    data = {
        "name": name,
        "description": "Tscheck product description",
        "active": str(active).lower(),
        "variants_json": '[{"id": "variant-1", "color": "Hitam", "model": "Standar", "size": "All Size", "price": 55000}]',
    }
    return client.post("/admin/products", data=data, files=files)


def test_create_product_appears_in_public_catalog(client):
    _login(client)
    name = "tscheck-product-create-1"
    resp = _create_product(client, name, active=True)
    assert resp.status_code == 200, f"product creation failed: {resp.status_code} {resp.text}"
    product = resp.json()
    product_id = product["id"]
    assert product["active"] is True
    assert product["editable"] is True

    public = client.get("/products")
    assert public.status_code == 200
    assert any(p["id"] == product_id for p in public.json()), "created active product missing from public /products"


def test_edit_deactivate_hides_from_public_then_delete_removes(client):
    _login(client)
    name = "tscheck-product-edit-1"
    created = _create_product(client, name, active=True).json()
    product_id = created["id"]

    # deactivate via update
    update_payload = {
        "name": name,
        "description": "Updated description",
        "active": False,
        "variants": created["variants"],
    }
    update_resp = client.put(f"/admin/products/{product_id}", json=update_payload)
    assert update_resp.status_code == 200, f"update failed: {update_resp.status_code} {update_resp.text}"
    assert update_resp.json()["active"] is False

    public_after_deactivate = client.get("/products")
    assert not any(p["id"] == product_id for p in public_after_deactivate.json()), "inactive product still shown publicly"

    admin_products = client.get("/admin/products")
    assert any(p["id"] == product_id for p in admin_products.json()), "admin product list should still include inactive product"

    delete_resp = client.delete(f"/admin/products/{product_id}")
    assert delete_resp.status_code == 204, f"delete failed: {delete_resp.status_code} {delete_resp.text}"

    admin_after_delete = client.get("/admin/products")
    assert not any(p["id"] == product_id for p in admin_after_delete.json()), "deleted product still present"


def test_builtin_product_cannot_be_deleted(client):
    _login(client)
    resp = client.delete("/admin/products/kaos-bani-zainuddin")
    assert resp.status_code == 422, f"built-in product deletion should be rejected, got {resp.status_code}: {resp.text}"

    still_present = client.get("/products")
    assert any(p["id"] == "kaos-bani-zainuddin" for p in still_present.json()), "built-in product disappeared after rejected delete attempt"
