"""SQLite helpers shared by every feature module."""
import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db_path, modules):
    """Create the tables declared by each module (SCHEMA), then run their seed()."""
    conn = sqlite3.connect(db_path)
    try:
        for module in modules:
            schema = getattr(module, "SCHEMA", "")
            if schema:
                conn.executescript(schema)
        for module in modules:
            seed = getattr(module, "seed", None)
            if seed:
                seed(conn)
        conn.commit()
    finally:
        conn.close()
