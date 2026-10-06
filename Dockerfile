FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY pytest.ini .
COPY tests/ tests/

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

ENV DB_PATH=/app/aceest_fitness.db

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]
