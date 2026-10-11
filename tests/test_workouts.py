import pytest

from aceest.workouts import parse_exercise


def test_log_workout_and_read_history(client, make_client):
    make_client("Kabir")
    response = client.post(
        "/clients/Kabir/workouts",
        json={
            "date": "2026-10-01",
            "workout_type": "Cardio",
            "duration_min": 45,
            "notes": "5k run",
        },
    )
    assert response.status_code == 201
    history = client.get("/clients/Kabir/workouts").get_json()
    assert len(history) == 1
    assert history[0]["workout_type"] == "Cardio"
    assert history[0]["duration_min"] == 45
    assert history[0]["notes"] == "5k run"
    assert history[0]["exercises"] == []


def test_defaults_are_today_and_sixty_minutes(client, make_client):
    make_client("Kabir")
    client.post("/clients/Kabir/workouts", json={"workout_type": "Strength"})
    entry = client.get("/clients/Kabir/workouts").get_json()[0]
    assert entry["duration_min"] == 60
    assert len(entry["date"]) == 10


def test_exercise_details_are_stored_with_the_workout(client, make_client):
    make_client("Kabir")
    client.post(
        "/clients/Kabir/workouts",
        json={
            "workout_type": "Strength",
            "exercise": {"name": "Back Squat", "sets": 5, "reps": 5, "weight": 100},
        },
    )
    exercise = client.get("/clients/Kabir/workouts").get_json()[0]["exercises"][0]
    assert exercise == {"name": "Back Squat", "sets": 5, "reps": 5, "weight": 100.0}


def test_exercise_defaults_to_three_sets_of_ten(client, make_client):
    make_client("Kabir")
    client.post(
        "/clients/Kabir/workouts",
        json={"workout_type": "Strength", "exercise": {"name": "Push-Up"}},
    )
    exercise = client.get("/clients/Kabir/workouts").get_json()[0]["exercises"][0]
    assert (exercise["sets"], exercise["reps"], exercise["weight"]) == (3, 10, 0.0)


def test_workout_type_is_required_and_validated(client, make_client):
    make_client("Kabir")
    assert client.post("/clients/Kabir/workouts", json={}).status_code == 400
    response = client.post("/clients/Kabir/workouts", json={"workout_type": "Yoga"})
    assert response.status_code == 400
    assert "workout_type must be one of" in response.get_json()["error"]


def test_invalid_duration_and_date_are_rejected(client, make_client):
    make_client("Kabir")
    bad_duration = client.post(
        "/clients/Kabir/workouts", json={"workout_type": "Cardio", "duration_min": 0}
    )
    assert bad_duration.status_code == 400
    bad_date = client.post(
        "/clients/Kabir/workouts", json={"workout_type": "Cardio", "date": "tomorrow"}
    )
    assert bad_date.status_code == 400


def test_exercise_without_a_name_is_rejected(client, make_client):
    make_client("Kabir")
    response = client.post(
        "/clients/Kabir/workouts",
        json={"workout_type": "Strength", "exercise": {"sets": 3}},
    )
    assert response.status_code == 400


def test_parse_exercise_validation():
    assert parse_exercise(None) is None
    with pytest.raises(ValueError, match="exercise must be an object"):
        parse_exercise("squat")


def test_history_is_newest_first(client, make_client):
    make_client("Kabir")
    for day in ("2026-10-01", "2026-10-03", "2026-10-02"):
        client.post("/clients/Kabir/workouts", json={"workout_type": "Mobility", "date": day})
    dates = [item["date"] for item in client.get("/clients/Kabir/workouts").get_json()]
    assert dates == ["2026-10-03", "2026-10-02", "2026-10-01"]


def test_workouts_for_unknown_client_return_404(client):
    response = client.post("/clients/Nobody/workouts", json={"workout_type": "Cardio"})
    assert response.status_code == 404
    assert client.get("/clients/Nobody/workouts").status_code == 404
