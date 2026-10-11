FROM python:3.11-slim

WORKDIR /app

# Dependency layer cached separately from source changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY pytest.ini .
COPY aceest/ aceest/
COPY tests/ tests/

# Run as non-root. The SQLite file lives under /tmp, which is writable
# by any user, so a root-owned /app never blocks the app from starting.
RUN useradd --create-home --shell /bin/bash appuser
ENV DB_PATH=/tmp/aceest_fitness.db
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
