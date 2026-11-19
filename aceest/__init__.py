"""ACEest Fitness & Gym - Flask application factory."""
import os
from typing import Optional

from flask import Flask

from . import (
    analytics,
    auth,
    bmi,
    clients,
    dashboard,
    db,
    health,
    membership,
    meta,
    metrics,
    program_generator,
    programs,
    progress,
    reports,
    versions,
    workouts,
)

# Registration order = the order the features were built.
MODULES = [
    health,
    auth,
    programs,
    clients,
    bmi,
    membership,
    workouts,
    metrics,
    progress,
    dashboard,
    reports,
    program_generator,
    analytics,
]


def create_app(db_path: Optional[str] = None, version: Optional[str] = None) -> Flask:
    """Build the app for one release (default: APP_VERSION env var, else the latest)."""
    release = versions.canonical(version or os.environ.get("APP_VERSION", versions.LATEST))
    enabled = set(versions.module_names(release))
    active = [m for m in MODULES if m.__name__.rsplit(".", 1)[-1] in enabled]

    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "aceest_fitness.db")
    app.config["APP_VERSION"] = release
    app.config["APP_MODULES"] = [m.__name__.rsplit(".", 1)[-1] for m in active]
    app.teardown_appcontext(db.close_db)
    for module in active:
        app.register_blueprint(module.bp)
    app.register_blueprint(meta.bp)
    db.init_db(app.config["DB_PATH"], active)
    return app
