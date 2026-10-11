def test_summary_for_a_fresh_client(client, make_client):
    make_client("Ravi")
    body = client.get("/clients/Ravi/summary").get_json()
    assert body["name"] == "Ravi"
    assert body["weeks_logged"] == 0
    assert body["average_adherence"] is None
    assert body["last_metric"] is None
    assert body["bmi"] is None


def test_summary_aggregates_program_bmi_progress_and_metrics(client, make_client):
    make_client("Meera", height=160, weight=60, program="Beginner (BG)")
    client.post("/clients/Meera/progress", json={"week": "W1", "adherence": 70})
    client.post("/clients/Meera/progress", json={"week": "W2", "adherence": 90})
    client.post("/clients/Meera/metrics", json={"date": "2026-10-01", "weight": 59})
    body = client.get("/clients/Meera/summary").get_json()
    assert body["calories"] == 1534  # weight metric (59kg) recalculated calories
    assert body["bmi"] == {"value": 23.0, "category": "Normal"}  # weight 59kg after metric update
    assert body["weeks_logged"] == 2
    assert body["average_adherence"] == 80.0
    assert body["last_metric"]["weight"] == 59


def test_summary_unknown_client_returns_404(client):
    assert client.get("/clients/Nobody/summary").status_code == 404
