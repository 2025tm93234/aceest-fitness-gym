def test_new_client_membership_is_active_without_a_renewal_date(client, make_client):
    make_client("Divya")
    response = client.get("/clients/Divya/membership")
    assert response.status_code == 200
    assert response.get_json() == {
        "name": "Divya",
        "membership_status": "Active",
        "renewal_date": "N/A",
    }


def test_membership_shows_the_renewal_date(client, make_client):
    make_client("Divya", membership_status="Expired", membership_end="2026-12-31")
    body = client.get("/clients/Divya/membership").get_json()
    assert body["membership_status"] == "Expired"
    assert body["renewal_date"] == "2026-12-31"
