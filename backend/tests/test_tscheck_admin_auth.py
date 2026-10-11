"""Admin PIN login/logout and auth gating (criterion: admin area protected by six-digit PIN)."""

ADMIN_PIN = "492345"


def test_admin_login_wrong_pin_rejected(client):
    resp = client.post("/admin/login", json={"pin": "000000"})
    assert resp.status_code == 401, f"expected 401 for wrong PIN, got {resp.status_code}: {resp.text}"


def test_admin_orders_requires_auth(client):
    resp = client.get("/admin/orders")
    assert resp.status_code in (401, 403), f"unauthenticated admin orders should be rejected, got {resp.status_code}"


def test_admin_login_logout_flow(client):
    login = client.post("/admin/login", json={"pin": ADMIN_PIN})
    assert login.status_code == 200, f"correct PIN should login, got {login.status_code}: {login.text}"
    assert login.json()["authenticated"] is True

    session = client.get("/admin/session")
    assert session.status_code == 200
    assert session.json()["authenticated"] is True

    orders = client.get("/admin/orders")
    assert orders.status_code == 200, f"authenticated admin orders should succeed, got {orders.status_code}: {orders.text}"

    logout = client.post("/admin/logout")
    assert logout.status_code == 200
    assert logout.json()["authenticated"] is False

    session_after = client.get("/admin/session")
    assert session_after.json()["authenticated"] is False

    orders_after = client.get("/admin/orders")
    assert orders_after.status_code in (401, 403), "orders should be blocked again after logout"
