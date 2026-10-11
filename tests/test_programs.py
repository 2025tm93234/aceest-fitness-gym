from aceest.programs import PROGRAMS, calories_for


def test_catalog_lists_every_program(client):
    response = client.get("/programs")
    assert response.status_code == 200
    names = [item["name"] for item in response.get_json()]
    assert names == list(PROGRAMS)
    assert {"factor", "desc", "workout", "diet"} <= set(response.get_json()[0])


def test_calories_use_the_program_factor():
    assert calories_for("Fat Loss (FL) - 3 day", 78) == 1716
    assert calories_for("Muscle Gain (MG) - PPL", 70) == 2450
    assert calories_for("Beginner (BG)", 60.5) == 1573


def test_calories_need_a_known_program_and_a_weight():
    assert calories_for(None, 70) is None
    assert calories_for("Beginner (BG)", None) is None
    assert calories_for("Unknown plan", 70) is None
