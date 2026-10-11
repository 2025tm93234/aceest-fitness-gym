"""ACEest Fitness & Gym - Flask application factory."""
import os
from typing import Optional

from flask import Flask

from . import (
    db,
    health,
)

# Registration order = the order the features were built.
MODULES = [
    health,
]


def create_app(db_path: Optional[str] = None) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "aceest_fitness.db")
    app.teardown_appcontext(db.close_db)
    for module in MODULES:
        app.register_blueprint(module.bp)
    db.init_db(app.config["DB_PATH"], MODULES)
    return app
