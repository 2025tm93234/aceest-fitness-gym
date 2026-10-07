# ACEest Fitness & Gym — CI/CD Pipeline

A Flask web application developed independently for the BITS DevOps Assignment-1. The supplied ACEest Tkinter scripts were used as functional references.

## Local Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Application: http://127.0.0.1:5000

## Tests
```bash
pytest -v --cov=app
flake8 app.py tests/
```

## Docker
```bash
docker build -t aceest-fitness:local .
docker run -d -p 5000:5000 aceest-fitness:local
curl http://127.0.0.1:5000/health
```

## CI/CD
GitHub Actions runs on pushes and pull requests and performs Build & Lint, Docker Image Assembly, and Pytest inside the container. Jenkins on Prayogshala performs checkout, environment setup, lint, unit tests, and Docker build.

## Git History
The application was built using multiple meaningful feature branches and a hotfix branch. The six-feature sequence in the assignment guide is an implementation strategy, not an assignment-mandated feature count.

## Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/clients` | Create client |
| GET | `/clients` | List clients |
| GET | `/clients/<name>` | Get client |
| GET | `/clients/<name>/bmi` | BMI calculation |
| POST | `/clients/<name>/program` | Workout program generation |
| GET | `/clients/<name>/membership` | Membership status |
| POST/GET | `/clients/<name>/workouts` | Log/list workouts |
