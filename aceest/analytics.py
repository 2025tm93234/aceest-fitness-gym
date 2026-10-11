"""Gym-wide analytics overview, built only from data already collected."""
from flask import Blueprint, jsonify

from .db import get_db

bp = Blueprint("analytics", __name__)


@bp.get("/analytics/overview")
def overview():
    db = get_db()
    total_clients = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    active_clients = db.execute(
        "SELECT COUNT(*) FROM clients WHERE membership_status = 'Active'"
    ).fetchone()[0]
    by_program = db.execute(
        "SELECT COALESCE(program, 'Unassigned') AS program, COUNT(*) AS clients "
        "FROM clients GROUP BY program ORDER BY clients DESC, program"
    ).fetchall()
    avg_adherence_row = db.execute("SELECT AVG(adherence) FROM progress").fetchone()
    avg_adherence = round(avg_adherence_row[0], 1) if avg_adherence_row[0] is not None else None
    total_workouts = db.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]
    return jsonify(
        total_clients=total_clients,
        active_clients=active_clients,
        clients_by_program=[dict(row) for row in by_program],
        average_adherence_all_clients=avg_adherence,
        total_workouts_logged=total_workouts,
    ), 200
