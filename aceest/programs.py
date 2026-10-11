"""Program catalog (ACEest 2.x program list + 1.x plans) and the calorie helper."""
from typing import Optional

from flask import Blueprint, jsonify

bp = Blueprint("programs", __name__)

PROGRAMS = {
    "Fat Loss (FL) - 3 day": {
        "factor": 22,
        "desc": "3-day full-body fat loss",
        "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
        "diet": "Egg Whites, Chicken, Fish Curry",
    },
    "Fat Loss (FL) - 5 day": {
        "factor": 24,
        "desc": "5-day split, higher volume fat loss",
        "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
        "diet": "Egg Whites, Chicken, Fish Curry",
    },
    "Muscle Gain (MG) - PPL": {
        "factor": 35,
        "desc": "Push/Pull/Legs hypertrophy",
        "workout": "Squat, Bench, Deadlift, Press, Rows",
        "diet": "Eggs, Biryani, Mutton Curry",
    },
    "Beginner (BG)": {
        "factor": 26,
        "desc": "3-day simple beginner full-body",
        "workout": "Air Squats, Ring Rows, Push-ups",
        "diet": "Balanced Tamil Meals",
    },
}


def calories_for(program: Optional[str], weight: Optional[float]) -> Optional[int]:
    """Daily calories = body weight (kg) x the program's calorie factor."""
    if not program or not weight or program not in PROGRAMS:
        return None
    return int(weight * PROGRAMS[program]["factor"])


@bp.get("/programs")
def list_programs():
    return jsonify([dict(name=name, **details) for name, details in PROGRAMS.items()]), 200
