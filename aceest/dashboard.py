"""Client summary dashboard (ACEest 2.x/3.2.4 'Client Summary' tab)."""
from flask import Blueprint, jsonify

from .bmi import bmi_category, calculate_bmi
from .clients import find_client
from .db import get_db

bp = Blueprint("dashboard", __name__)


@bp.get("/clients/<name>/summary")
def client_summary(name):
    client = find_client(name)
    if client is None:
        return jsonify(error="client not found"), 404
    db = get_db()
    weeks, avg_adherence = db.execute(
        "SELECT COUNT(*), AVG(adherence) FROM progress WHERE client_name = ?", (name,)
    ).fetchone()
    avg_adherence = round(avg_adherence, 1) if avg_adherence is not None else None
    last_metric = db.execute(
        "SELECT date, weight, waist, bodyfat FROM metrics "
        "WHERE client_name = ? ORDER BY date DESC, id DESC LIMIT 1",
        (name,),
    ).fetchone()
    bmi = None
    if client["height"] and client["weight"]:
        value = calculate_bmi(client["weight"], client["height"])
        bmi = {"value": value, "category": bmi_category(value)[0]}
    return jsonify(
        name=name,
        program=client["program"],
        calories=client["calories"],
        membership_status=client["membership_status"],
        bmi=bmi,
        weeks_logged=weeks,
        average_adherence=avg_adherence,
        last_metric=dict(last_metric) if last_metric else None,
    ), 200
