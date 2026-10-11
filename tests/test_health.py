def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "ACEest" in response.get_json()["service"]
