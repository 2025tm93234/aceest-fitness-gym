
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

# Release selected at build time: docker build --build-arg APP_VERSION=2.2.1 ...
# Declared after the heavy layers so every version shares them in the build cache.
ARG APP_VERSION=3.2.4
ENV APP_VERSION=${APP_VERSION}
LABEL org.opencontainers.image.title="aceest-fitness" \
      org.opencontainers.image.version="${APP_VERSION}"

# Store the SQLite database in a writable temporary directory.
ENV DB_PATH=/tmp/aceest_fitness.db

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# WEB_CONCURRENCY lowers the worker count on small clusters; access log goes to stdout.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:5000 --workers ${WEB_CONCURRENCY:-2} --access-logfile - app:app"]
