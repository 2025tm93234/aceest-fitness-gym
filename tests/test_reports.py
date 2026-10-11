def test_csv_report_contains_the_client_row(client, make_client):
    make_client("Ravi", age=28, height=175, weight=78, program="Beginner (BG)")
    response = client.get("/clients/Ravi/report.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    body = response.get_data(as_text=True)
    assert "Ravi" in body and "Beginner (BG)" in body


def test_pdf_report_is_a_pdf_document(client, make_client):
    make_client("Ravi")
    response = client.get("/clients/Ravi/report.pdf")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.get_data()[:4] == b"%PDF"
