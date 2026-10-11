import pytest

from aceest.bmi import bmi_category, calculate_bmi


def test_calculate_bmi_uses_centimetres_and_rounds_to_one_decimal():
    assert calculate_bmi(60, 160) == 23.4
    assert calculate_bmi(78, 175) == 25.5


def test_calculate_bmi_rejects_non_positive_values():
    with pytest.raises(ValueError):
        calculate_bmi(0, 170)
    with pytest.raises(ValueError):
        calculate_bmi(70, -1)


@pytest.mark.parametrize(
    "bmi, category",
    [
        (18.4, "Underweight"),
        (18.5, "Normal"),
        (24.9, "Normal"),
        (25.0, "Overweight"),
        (29.9, "Overweight"),
        (30.0, "Obese"),
    ],
)
def test_bmi_category_boundaries(bmi, category):
    assert bmi_category(bmi)[0] == category


def test_bmi_endpoint_returns_category_and_risk(client, make_client):
    make_client("Meera", height=160, weight=60)
    response = client.get("/clients/Meera/bmi")
    assert response.status_code == 200
    body = response.get_json()
    assert body["bmi"] == 23.4
    assert body["category"] == "Normal"
    assert body["risk"] == "Low risk if active and strong."


def test_bmi_needs_height_and_weight(client, make_client):
    make_client("NoStats")
    response = client.get("/clients/NoStats/bmi")
    assert response.status_code == 400


def test_bmi_unknown_client_returns_404(client):
    assert client.get("/clients/Nobody/bmi").status_code == 404
