def test_log_all_three_measurements(client, make_client):
    make_client("Ravi")
    response = client.post(
        "/clients/Ravi/metrics",
        json={"date": "2026-10-01", "weight": 78.5, "waist": 88, "bodyfat": 21.5},
    )
    assert response.status_code == 201
    assert response.get_json() == {
        "name": "Ravi",
        "date": "2026-10-01",
        "weight": 78.5,
        "waist": 88.0,
        "bodyfat": 21.5,
    }


def test_date_defaults_to_today(client, make_client):
    make_client("Ravi")
    body = client.post("/clients/Ravi/metrics", json={"waist": 90}).get_json()
    assert len(body["date"]) == 10


def test_at_least_one_measurement_is_required(client, make_client):
    make_client("Ravi")
    response = client.post("/clients/Ravi/metrics", json={"date": "2026-10-01"})
    assert response.status_code == 400


def test_invalid_measurements_and_dates_are_rejected(client, make_client):
    make_client("Ravi")
    assert client.post("/clients/Ravi/metrics", json={"weight": -4}).status_code == 400
    assert client.post("/clients/Ravi/metrics", json={"weight": "x"}).status_code == 400
    bad_date = client.post("/clients/Ravi/metrics", json={"date": "1/2/2026", "weight": 70})
    assert bad_date.status_code == 400


def test_new_weight_updates_client_weight_and_calories(client, make_client):
    make_client("Ravi", weight=70, program="Beginner (BG)")
    client.post("/clients/Ravi/metrics", json={"date": "2026-10-01", "weight": 65})
    updated = client.get("/clients/Ravi").get_json()
    assert updated["weight"] == 65
    assert updated["calories"] == 1690


def test_waist_only_entry_leaves_client_weight_alone(client, make_client):
    make_client("Ravi", weight=70)
    client.post("/clients/Ravi/metrics", json={"waist": 85})
    assert client.get("/clients/Ravi").get_json()["weight"] == 70


def test_metrics_for_unknown_client_return_404(client):
    assert client.post("/clients/Nobody/metrics", json={"weight": 70}).status_code == 404
    assert client.get("/clients/Nobody/metrics").status_code == 404
    assert client.get("/clients/Nobody/metrics/weight-chart").status_code == 404


def test_list_metrics_is_ordered_by_date(client, make_client):
    make_client("Ravi")
    client.post("/clients/Ravi/metrics", json={"date": "2026-10-05", "weight": 77})
    client.post("/clients/Ravi/metrics", json={"date": "2026-10-01", "weight": 78})
    dates = [row["date"] for row in client.get("/clients/Ravi/metrics").get_json()]
    assert dates == ["2026-10-01", "2026-10-05"]


def test_weight_chart_skips_entries_without_weight(client, make_client):
    make_client("Ravi")
    client.post("/clients/Ravi/metrics", json={"date": "2026-10-01", "weight": 78})
    client.post("/clients/Ravi/metrics", json={"date": "2026-10-02", "waist": 90})
    client.post("/clients/Ravi/metrics", json={"date": "2026-10-03", "weight": 77})
    chart = client.get("/clients/Ravi/metrics/weight-chart").get_json()
    assert chart["title"] == "Weight Trend - Ravi"
    assert chart["labels"] == ["2026-10-01", "2026-10-03"]
    assert chart["values"] == [78.0, 77.0]


def test_weight_chart_without_data_explains_why(client, make_client):
    make_client("Ravi")
    chart = client.get("/clients/Ravi/metrics/weight-chart").get_json()
    assert chart["values"] == []
    assert chart["message"] == "No weight metrics available for this client"
