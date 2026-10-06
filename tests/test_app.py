import os
import tempfile

import pytest

from app import bmi_category, calculate_bmi, create_app


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


def test_generate_program_valid_type(client):
    client.post("/clients", json={"name": "Arjun"})
    response = client.post(
        "/clients/Arjun/program", json={"program_type": "Muscle Gain"}
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["program_type"] == "Muscle Gain"
    assert body["program"]


def test_generate_program_invalid_type(client):
    client.post("/clients", json={"name": "Arjun"})
    response = client.post(
        "/clients/Arjun/program", json={"program_type": "Bulk"}
    )
    assert response.status_code == 400


def test_generate_program_unknown_client(client):
    response = client.post(
        "/clients/Nobody/program", json={"program_type": "Beginner"}
    )
    assert response.status_code == 404


def test_membership_check(client):
    client.post("/clients", json={"name": "Divya"})
    response = client.get("/clients/Divya/membership")
    assert response.status_code == 200
    assert response.get_json()["membership_status"] == "Active"


def test_add_and_list_workout(client):
    client.post("/clients", json={"name": "Kabir"})
    response = client.post(
        "/clients/Kabir/workouts",
        json={"date": "2026-01-10", "workout_type": "Cardio", "duration_min": 45},
    )
    assert response.status_code == 201
    response = client.get("/clients/Kabir/workouts")
    assert response.status_code == 200
    workouts = response.get_json()
    assert len(workouts) == 1
    assert workouts[0]["workout_type"] == "Cardio"


def test_workout_unknown_client(client):
    response = client.post(
        "/clients/Nobody/workouts",
        json={"workout_type": "Cardio"},
    )
    assert response.status_code == 404


def test_list_workouts_unknown_client(client):
    response = client.get("/clients/Nobody/workouts")
    assert response.status_code == 404


def test_membership_check_not_found(client):
    response = client.get("/clients/Nobody/membership")
    assert response.status_code == 404
