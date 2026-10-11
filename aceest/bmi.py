"""BMI & risk info (ACEest 2.2.4 'BMI & Risk Info' button)."""
from typing import Tuple

from flask import Blueprint, jsonify

from .clients import find_client

bp = Blueprint("bmi", __name__)


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("weight and height must be positive")
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m * height_m), 1)


def bmi_category(bmi: float) -> Tuple[str, str]:
    if bmi < 18.5:
        return "Underweight", "Potential nutrient deficiency, low energy."
    if bmi < 25:
        return "Normal", "Low risk if active and strong."
    if bmi < 30:
        return "Overweight", "Moderate risk; focus on adherence and progressive activity."
    return "Obese", "Higher risk; prioritize fat loss, consistency, and supervision."


@bp.get("/clients/<name>/bmi")
def client_bmi(name):
    client = find_client(name)
    if client is None:
        return jsonify(error="client not found"), 404
    if not client["height"] or not client["weight"]:
        return jsonify(error="height and weight are required to calculate BMI"), 400
    bmi = calculate_bmi(client["weight"], client["height"])
    category, risk = bmi_category(bmi)
    return jsonify(name=name, bmi=bmi, category=category, risk=risk), 200
