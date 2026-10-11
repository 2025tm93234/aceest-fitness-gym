def test_overview_on_an_empty_database(client):
    body = client.get("/analytics/overview").get_json()
    assert body == {
        "total_clients": 0,
        "active_clients": 0,
        "clients_by_program": [],
        "average_adherence_all_clients": None,
        "total_workouts_logged": 0,
    }


def test_overview_aggregates_across_clients(client, make_client):
    make_client("Ravi", program="Beginner (BG)")
    make_client("Meera", program="Beginner (BG)")
    make_client("Arjun", program="Muscle Gain (MG) - PPL", membership_status="Expired")
    client.post("/clients/Ravi/progress", json={"week": "W1", "adherence": 60})
    client.post("/clients/Meera/progress", json={"week": "W1", "adherence": 100})
    client.post("/clients/Ravi/workouts", json={"workout_type": "Cardio"})
    body = client.get("/analytics/overview").get_json()
    assert body["total_clients"] == 3
    assert body["active_clients"] == 2
    assert body["average_adherence_all_clients"] == 80.0
    assert body["total_workouts_logged"] == 1
    programs = {row["program"]: row["clients"] for row in body["clients_by_program"]}
    assert programs["Beginner (BG)"] == 2
    assert programs["Muscle Gain (MG) - PPL"] == 1
