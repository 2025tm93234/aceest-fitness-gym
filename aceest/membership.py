"""Membership check (ACEest 3.2.4 'Check Membership' button)."""
from flask import Blueprint, jsonify

from .db import get_db

bp = Blueprint("membership", __name__)


@bp.get("/clients/<name>/membership")
def check_membership(name):
    row = get_db().execute(
        "SELECT membership_status, membership_end FROM clients WHERE name = ?", (name,)
    ).fetchone()
    if row is None:
        return jsonify(error="client not found"), 404
    return jsonify(
        name=name,
        membership_status=row["membership_status"],
        renewal_date=row["membership_end"] or "N/A",
    ), 200
