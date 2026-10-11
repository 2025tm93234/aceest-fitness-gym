
FROM python:3.11-slim

WORKDIR /app

# Create the non-root application user first.
RUN useradd --create-home --shell /bin/bash appuser

# Dependency layer cached separately from source changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY pytest.ini .
COPY aceest/ aceest/
COPY tests/ tests/

# Allow appuser to write application files, pytest cache and coverage data.
RUN chown -R appuser:appuser /app

# Store the SQLite database in a writable temporary directory.
ENV DB_PATH=/tmp/aceest_fitness.db

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]

