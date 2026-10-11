def test_default_admin_can_log_in(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert response.get_json() == {"username": "admin", "role": "Admin"}


def test_login_strips_surrounding_whitespace(client):
    response = client.post("/auth/login", json={"username": " admin ", "password": " admin "})
    assert response.status_code == 200


def test_wrong_password_is_rejected(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "nope"})
    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid credentials"


def test_unknown_user_is_rejected(client):
    response = client.post("/auth/login", json={"username": "ghost", "password": "admin"})
    assert response.status_code == 401


def test_missing_credentials_return_400(client):
    assert client.post("/auth/login", json={"username": "admin"}).status_code == 400
    assert client.post("/auth/login", json={}).status_code == 400
    assert client.post("/auth/login").status_code == 400


def test_password_is_stored_hashed(app):
    import sqlite3

    conn = sqlite3.connect(app.config["DB_PATH"])
    stored = conn.execute("SELECT password_hash FROM users WHERE username = 'admin'").fetchone()
    conn.close()
    assert stored[0] != "admin"
    assert stored[0].startswith("pbkdf2:")
