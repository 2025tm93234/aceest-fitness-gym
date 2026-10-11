"""Program generation: random template (ACEest 3.2.4) and the experience-based plan (3.1.2)."""
import random

from flask import Blueprint, jsonify

from .clients import find_client
from .db import get_db
from .util import json_body

bp = Blueprint("program_generator", __name__)

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}

EXERCISE_POOL = {
    "Strength": ["Squat", "Deadlift", "Bench Press", "Overhead Press", "Pull-Up", "Barbell Row"],
    "Hypertrophy": [
        "Leg Press",
        "Incline Dumbbell Press",
        "Lat Pulldown",
        "Lateral Raise",
        "Bicep Curl",
        "Tricep Extension",
    ],
    "Conditioning": ["Running", "Cycling", "Rowing", "Burpees", "Jump Rope", "Kettlebell Swings"],
    "Full Body": ["Push-Up", "Pull-Up", "Lunge", "Plank", "Dumbbell Row", "Dumbbell Press"],
}

EXPERIENCE_LEVELS = {
    "beginner": {"sets": (2, 3), "reps": (8, 12), "days": 3},
    "intermediate": {"sets": (3, 4), "reps": (8, 15), "days": 4},
    "advanced": {"sets": (4, 5), "reps": (6, 15), "days": 5},
}

WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def focus_for(program_name):
    program_name = program_name or ""
    if "Fat Loss" in program_name:
        return "Conditioning"
    if "Muscle Gain" in program_name:
        return "Hypertrophy"
    return "Full Body"


def build_plan(program_name, experience):
    level = EXPERIENCE_LEVELS[experience]
    focus = focus_for(program_name)
    per_day = 3 if level["days"] < 4 else 4
    plan = []
    for day in WEEK_DAYS[: level["days"]]:
        exercises = [
            {
                "name": exercise,
                "sets": random.randint(*level["sets"]),
                "reps": random.randint(*level["reps"]),
            }
            for exercise in random.sample(EXERCISE_POOL[focus], k=per_day)
        ]
        plan.append({"day": day, "exercises": exercises})
    return focus, plan


@bp.post("/clients/<name>/program")
def generate_program(name):
    if find_client(name) is None:
        return jsonify(error="client not found"), 404
    program_type = json_body().get("program_type") or random.choice(list(PROGRAM_TEMPLATES))
    if program_type not in PROGRAM_TEMPLATES:
        return jsonify(error="program_type must be one of: " + ", ".join(PROGRAM_TEMPLATES)), 400
    detail = random.choice(PROGRAM_TEMPLATES[program_type])
    db = get_db()
    db.execute("UPDATE clients SET program = ? WHERE name = ?", (detail, name))
    db.commit()
    return jsonify(name=name, program_type=program_type, program=detail), 200


@bp.post("/clients/<name>/ai-program")
def generate_ai_program(name):
    client = find_client(name)
    if client is None:
        return jsonify(error="client not found"), 404
    experience = str(json_body().get("experience") or "").strip().lower()
    if experience not in EXPERIENCE_LEVELS:
        return jsonify(error="experience must be one of: " + ", ".join(EXPERIENCE_LEVELS)), 400
    focus, plan = build_plan(client["program"], experience)
    return jsonify(name=name, experience=experience, focus=focus, plan=plan), 200
