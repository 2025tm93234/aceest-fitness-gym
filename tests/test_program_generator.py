import pytest

from aceest.program_generator import (
    EXERCISE_POOL,
    EXPERIENCE_LEVELS,
    PROGRAM_TEMPLATES,
    build_plan,
    focus_for,
)


def test_generate_program_for_a_chosen_type_updates_the_client(client, make_client):
    make_client("Arjun")
    response = client.post("/clients/Arjun/program", json={"program_type": "Muscle Gain"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["program_type"] == "Muscle Gain"
    assert body["program"] in PROGRAM_TEMPLATES["Muscle Gain"]
    assert client.get("/clients/Arjun").get_json()["program"] == body["program"]


def test_generate_program_without_a_type_picks_one_at_random(client, make_client):
    make_client("Arjun")
    body = client.post("/clients/Arjun/program").get_json()
    assert body["program_type"] in PROGRAM_TEMPLATES
    assert body["program"] in PROGRAM_TEMPLATES[body["program_type"]]


def test_generate_program_rejects_unknown_type(client, make_client):
    make_client("Arjun")
    response = client.post("/clients/Arjun/program", json={"program_type": "Bulk"})
    assert response.status_code == 400


def test_generate_program_unknown_client_returns_404(client):
    assert client.post("/clients/Nobody/program").status_code == 404


@pytest.mark.parametrize(
    "program, focus",
    [
        ("Fat Loss (FL) - 5 day", "Conditioning"),
        ("Muscle Gain (MG) - PPL", "Hypertrophy"),
        ("Beginner (BG)", "Full Body"),
        (None, "Full Body"),
    ],
)
def test_focus_follows_the_client_program(program, focus):
    assert focus_for(program) == focus


@pytest.mark.parametrize(
    "experience, days, per_day",
    [("beginner", 3, 3), ("intermediate", 4, 4), ("advanced", 5, 4)],
)
def test_plan_shape_follows_experience(experience, days, per_day):
    _, plan = build_plan("Beginner (BG)", experience)
    assert len(plan) == days
    assert all(len(day["exercises"]) == per_day for day in plan)


def test_plan_sets_and_reps_stay_within_the_level_ranges():
    level = EXPERIENCE_LEVELS["intermediate"]
    _, plan = build_plan("Muscle Gain (MG) - PPL", "intermediate")
    for day in plan:
        for exercise in day["exercises"]:
            assert level["sets"][0] <= exercise["sets"] <= level["sets"][1]
            assert level["reps"][0] <= exercise["reps"] <= level["reps"][1]
            assert exercise["name"] in EXERCISE_POOL["Hypertrophy"]


def test_ai_program_endpoint_uses_the_clients_program(client, make_client):
    make_client("Arjun", program="Fat Loss (FL) - 3 day")
    response = client.post("/clients/Arjun/ai-program", json={"experience": "Beginner"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["focus"] == "Conditioning"
    assert body["experience"] == "beginner"
    assert [day["day"] for day in body["plan"]] == ["Monday", "Tuesday", "Wednesday"]


def test_ai_program_requires_a_valid_experience_level(client, make_client):
    make_client("Arjun")
    assert client.post("/clients/Arjun/ai-program", json={}).status_code == 400
    bad_level = client.post("/clients/Arjun/ai-program", json={"experience": "expert"})
    assert bad_level.status_code == 400


def test_ai_program_unknown_client_returns_404(client):
    response = client.post("/clients/Nobody/ai-program", json={"experience": "beginner"})
    assert response.status_code == 404
