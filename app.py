"""
ACEest Fitness & Gym - Flask Application
Independent Flask implementation for the ACEest Fitness & Gym assignment.
The supplied Tkinter versions are used as functional references; the Flask
application is built incrementally and kept testable/containerizable.
"""
import os
import sqlite3

from flask import Flask, jsonify, g

DB_PATH = os.environ.get("DB_PATH", "aceest_fitness.db")


def create_app(db_path: str = None) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or DB_PATH

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        conn = sqlite3.connect(app.config["DB_PATH"])
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                height REAL,
                weight REAL,
                program TEXT,
                membership_status TEXT DEFAULT 'Active'
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                date TEXT NOT NULL,
                workout_type TEXT,
                duration_min INTEGER,
                notes TEXT
            )
        """)
        conn.commit()
        conn.close()

    app.init_db = init_db
    app.get_db = get_db

    @app.route("/")
    def home():
        return jsonify(service="ACEest Fitness & Gym API", status="running")

    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    init_db()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
