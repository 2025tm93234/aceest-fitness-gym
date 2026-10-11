"""CSV and PDF client reports (ACEest 1.1.2 CSV export, 3.1.2/3.2.4 PDF report)."""
import csv
import io

from flask import Blueprint, Response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .clients import find_client

bp = Blueprint("reports", __name__)


@bp.get("/clients/<name>/report.csv")
def client_report_csv(name):
    client = find_client(name)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Name", "Age", "Height", "Weight", "Program", "Calories", "Membership"])
    writer.writerow(
        [
            client["name"],
            client["age"],
            client["height"],
            client["weight"],
            client["program"],
            client["calories"],
            client["membership_status"],
        ]
    )
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename={}_report.csv".format(name)},
    )


@bp.get("/clients/<name>/report.pdf")
def client_report_pdf(name):
    client = find_client(name)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 800, "ACEest Client Report - {}".format(client["name"]))
    pdf.setFont("Helvetica", 12)
    fields = [
        ("Age", client["age"]),
        ("Height", client["height"]),
        ("Weight", client["weight"]),
        ("Program", client["program"]),
        ("Calories", client["calories"]),
        ("Membership", client["membership_status"]),
    ]
    y = 760
    for label, value in fields:
        pdf.drawString(40, y, "{}: {}".format(label, value if value is not None else "-"))
        y -= 20
    pdf.showPage()
    pdf.save()
    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename={}_report.pdf".format(name)},
    )
