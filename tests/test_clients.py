def test_create_minimal_client_defaults_to_active(client):
    response = client.post("/clients", json={"name": "Ravi"})
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Ravi"
    assert body["membership_status"] == "Active"
    assert body["calories"] is None


def test_create_client_with_program_calculates_calories(client):
    payload = {
        "name": "Meera",
        "age": 29,
        "height": 160,
        "weight": 60,
        "program": "Beginner (BG)",
        "target_weight": 57,
        "target_adherence": 90,
        "notes": "Knee care",
    }
    response = client.post("/clients", json=payload)
    assert response.status_code == 201
    body = response.get_json()
    assert body["calories"] == 1560
    assert body["target_adherence"] == 90
    assert body["notes"] == "Knee care"


def test_duplicate_client_is_rejected(client, make_client):
    make_client("Ravi")
    response = client.post("/clients", json={"name": "Ravi"})
    assert response.status_code == 409


def test_name_is_required(client):
    assert client.post("/clients", json={"age": 30}).status_code == 400
    assert client.post("/clients", json={"name": "   "}).status_code == 400
    assert client.post("/clients").status_code == 400


def test_unknown_program_is_rejected(client):
    response = client.post("/clients", json={"name": "Ravi", "program": "Bulk"})
    assert response.status_code == 400
    assert "program must be one of" in response.get_json()["error"]


def test_invalid_numbers_are_rejected(client):
    assert client.post("/clients", json={"name": "A", "age": "abc"}).status_code == 400
    assert client.post("/clients", json={"name": "B", "weight": -5}).status_code == 400
    assert client.post("/clients", json={"name": "C", "target_adherence": 150}).status_code == 400


def test_membership_end_must_be_an_iso_date(client):
    bad = client.post("/clients", json={"name": "A", "membership_end": "31/12/2026"})
    assert bad.status_code == 400
    good = client.post("/clients", json={"name": "B", "membership_end": "2026-12-31"})
    assert good.status_code == 201
    assert good.get_json()["membership_end"] == "2026-12-31"


def test_list_clients_is_sorted_by_name(client, make_client):
    make_client("Zoya")
    make_client("Arun")
    names = [item["name"] for item in client.get("/clients").get_json()]
    assert names == ["Arun", "Zoya"]


def test_get_client_and_not_found(client, make_client):
    make_client("Ravi", age=28)
    assert client.get("/clients/Ravi").get_json()["age"] == 28
    assert client.get("/clients/Nobody").status_code == 404


def test_update_client_recalculates_calories(client, make_client):
    make_client("Ravi", weight=70, program="Beginner (BG)")
    response = client.put(
        "/clients/Ravi", json={"program": "Muscle Gain (MG) - PPL", "weight": 80}
    )
    assert response.status_code == 200
    assert response.get_json()["calories"] == 2800


def test_update_unknown_client_returns_404(client):
    assert client.put("/clients/Nobody", json={"age": 30}).status_code == 404


def test_update_without_fields_returns_400(client, make_client):
    make_client("Ravi")
    assert client.put("/clients/Ravi", json={}).status_code == 400


def test_update_with_invalid_value_returns_400(client, make_client):
    make_client("Ravi")
    assert client.put("/clients/Ravi", json={"age": -3}).status_code == 400
