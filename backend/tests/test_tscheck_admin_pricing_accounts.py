"""Admin can manage final per-variant prices and transfer accounts (criterion: admin manages
prices/accounts/images). Original values are restored after the test to avoid corrupting the
public catalog's seed state for other checks."""

ADMIN_PIN = "492345"


def _login(client):
    resp = client.post("/admin/login", json={"pin": ADMIN_PIN})
    assert resp.status_code == 200


def test_admin_updates_pricing_and_accounts_then_restores(client):
    _login(client)

    original = client.get("/admin/settings")
    assert original.status_code == 200, original.text
    original_pricing = original.json()["pricing"]
    original_accounts = original.json()["accounts"]

    try:
        probe_key = "S_pendek"
        new_pricing = dict(original_pricing)
        new_pricing["prices"] = dict(original_pricing["prices"])
        probe_value = original_pricing["prices"][probe_key] + 1000
        new_pricing["prices"][probe_key] = probe_value

        update_resp = client.patch("/admin/pricing", json=new_pricing)
        assert update_resp.status_code == 200, f"pricing update failed: {update_resp.status_code} {update_resp.text}"
        assert update_resp.json()["prices"][probe_key] == probe_value

        catalog_after = client.get("/catalog")
        assert catalog_after.status_code == 200
        assert catalog_after.json()["pricing"]["prices"][probe_key] == probe_value, "public catalog did not reflect updated price"

        test_account = {"id": "tscheck-bri-test", "bank": "BRI-TEST", "account_number": "9999999999", "account_name": "Tscheck Tester"}
        accounts_resp = client.put("/admin/accounts", json={"accounts": [test_account]})
        assert accounts_resp.status_code == 200, f"accounts update failed: {accounts_resp.status_code} {accounts_resp.text}"
        saved_accounts = accounts_resp.json()
        assert any(a["account_number"] == "9999999999" for a in saved_accounts)

        catalog_accounts = client.get("/catalog")
        transfer_accounts = next(m["accounts"] for m in catalog_accounts.json()["payment_methods"] if m["id"] == "transfer")
        assert any(a["account_number"] == "9999999999" for a in transfer_accounts), "public catalog did not reflect updated account"
    finally:
        client.patch("/admin/pricing", json=original_pricing)
        client.put("/admin/accounts", json={"accounts": original_accounts})
