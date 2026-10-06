import os
import tempfile

import pytest

from app import create_app


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app = create_app(db_path=db_path)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client
    os.close(db_fd)
    os.unlink(db_path)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "ACEest" in response.get_json()["service"]


def test_add_and_get_client(client):
    response = client.post(
        "/clients",
        json={"name": "Ravi", "age": 28, "height": 1.75, "weight": 78},
    )
    assert response.status_code == 201
    response = client.get("/clients/Ravi")
    assert response.status_code == 200
    body = response.get_json()
    assert body["name"] == "Ravi"
    assert body["membership_status"] == "Active"


def test_list_clients(client):
    client.post("/clients", json={"name": "Ravi"})
    client.post("/clients", json={"name": "Meera"})
    response = client.get("/clients")
    assert response.status_code == 200
    assert {row["name"] for row in response.get_json()} == {"Ravi", "Meera"}


def test_duplicate_client_rejected(client):
    client.post("/clients", json={"name": "Ravi"})
    response = client.post("/clients", json={"name": "Ravi"})
    assert response.status_code == 409


def test_missing_name_rejected(client):
    response = client.post("/clients", json={"age": 30})
    assert response.status_code == 400


def test_client_not_found(client):
    response = client.get("/clients/Nobody")
    assert response.status_code == 404


from app import bmi_category, calculate_bmi


def test_bmi_calculation(client):
    client.post("/clients", json={"name": "Meera", "height": 1.60, "weight": 60})
    response = client.get("/clients/Meera/bmi")
    assert response.status_code == 200
    body = response.get_json()
    assert body["bmi"] == 23.44
    assert body["category"] == "Normal"


def test_bmi_missing_data(client):
    client.post("/clients", json={"name": "NoStats"})
    response = client.get("/clients/NoStats/bmi")
    assert response.status_code == 400


def test_bmi_rejects_invalid_height():
    with pytest.raises(ValueError):
        calculate_bmi(60, 0)


def test_bmi_categories():
    assert bmi_category(18.4) == "Underweight"
    assert bmi_category(24.9) == "Normal"
    assert bmi_category(29.9) == "Overweight"
    assert bmi_category(30.0) == "Obese"
