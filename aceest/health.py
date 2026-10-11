"""Liveness endpoints."""
from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/")
def home():
    return jsonify(service="ACEest Fitness & Gym API", status="running")


@bp.get("/health")
def health():
    return jsonify(status="ok"), 200
