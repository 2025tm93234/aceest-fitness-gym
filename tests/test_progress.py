import pytest

from aceest.progress import parse_adherence


def test_log_progress_with_explicit_week(client, make_client):
    make_client("Ravi")
    response = client.post(
        "/clients/Ravi/progress", json={"week": "Week 40 - 2026", "adherence": 80}
    )
    assert response.status_code == 201
    assert response.get_json() == {"name": "Ravi", "week": "Week 40 - 2026", "adherence": 80}


def test_log_progress_defaults_the_week_label(client, make_client):
    make_client("Ravi")
    body = client.post("/clients/Ravi/progress", json={"adherence": 70}).get_json()
    assert body["week"].startswith("Week ")


@pytest.mark.parametrize("bad", [None, -1, 101, "abc", True])
def test_parse_adherence_rejects_invalid_values(bad):
    with pytest.raises(ValueError):
        parse_adherence(bad)


def test_log_progress_rejects_out_of_range_adherence(client, make_client):
    make_client("Ravi")
    assert client.post("/clients/Ravi/progress", json={"adherence": 140}).status_code == 400
    assert client.post("/clients/Ravi/progress", json={}).status_code == 400


def test_progress_for_unknown_client_returns_404(client):
    assert client.post("/clients/Nobody/progress", json={"adherence": 50}).status_code == 404
    assert client.get("/clients/Nobody/progress").status_code == 404
    assert client.get("/clients/Nobody/progress/chart").status_code == 404


def test_list_progress_keeps_insertion_order(client, make_client):
    make_client("Ravi")
    for week, value in [("W1", 60), ("W2", 75), ("W3", 90)]:
        client.post("/clients/Ravi/progress", json={"week": week, "adherence": value})
    rows = client.get("/clients/Ravi/progress").get_json()
    assert [row["week"] for row in rows] == ["W1", "W2", "W3"]


def test_progress_chart_data(client, make_client):
    make_client("Ravi")
    client.post("/clients/Ravi/progress", json={"week": "W1", "adherence": 60})
    client.post("/clients/Ravi/progress", json={"week": "W2", "adherence": 90})
    chart = client.get("/clients/Ravi/progress/chart").get_json()
    assert chart["title"] == "Weekly Adherence - Ravi"
    assert chart["labels"] == ["W1", "W2"]
    assert chart["values"] == [60, 90]
    assert (chart["y_min"], chart["y_max"]) == (0, 100)
    assert chart["message"] is None


def test_progress_chart_without_data_explains_why(client, make_client):
    make_client("Ravi")
    chart = client.get("/clients/Ravi/progress/chart").get_json()
    assert chart["labels"] == [] and chart["values"] == []
    assert chart["message"] == "No progress data available for this client"
