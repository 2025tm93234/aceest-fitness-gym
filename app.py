"""Entry point: `python app.py` for development, `gunicorn app:app` in Docker."""
from aceest import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
