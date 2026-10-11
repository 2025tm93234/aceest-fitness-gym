# ACEest Fitness & Gym - CI/CD Pipeline

A Flask web service for gym management: client records, login, BMI,
calorie-aware program generation, membership status, workout and exercise
logging, body metrics, weekly progress tracking, a client summary
dashboard, CSV/PDF report export, and a gym-wide analytics overview.
Containerized with Docker and built through both Jenkins and GitHub
Actions.

## Project Structure

| Path | Purpose |
|---|---|
| `app.py` | WSGI entry point (`app = create_app()`) |
| `aceest/__init__.py` | Application factory; registers every feature blueprint |
| `aceest/db.py` | SQLite connection and schema/seed wiring |
| `aceest/util.py` | Shared validation helpers |
| `aceest/auth.py` | Login (seeded `admin`/`admin` account) |
| `aceest/clients.py` | Client create/list/get/update |
| `aceest/programs.py` | Program catalog and calorie factors |
| `aceest/bmi.py` | BMI calculation and risk category |
| `aceest/membership.py` | Membership status check |
| `aceest/workouts.py` | Workout logging and history, with exercises |
| `aceest/metrics.py` | Body metrics logging and weight-trend chart data |
| `aceest/progress.py` | Weekly adherence logging and chart data |
| `aceest/dashboard.py` | Per-client summary |
| `aceest/reports.py` | CSV and PDF client reports |
| `aceest/program_generator.py` | Randomized and experience-based program generation |
| `aceest/analytics.py` | Gym-wide analytics overview |
| `tests/` | Pytest suite, one file per feature |
| `Dockerfile` / `.dockerignore` | Container build |
| `Jenkinsfile` | Jenkins declarative pipeline (runs on Prayogshala) |
| `.github/workflows/main.yml` | GitHub Actions pipeline |

## Local Setup & Execution

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# App runs at http://127.0.0.1:5000
```

## Running Tests Manually

```bash
python -m flake8 aceest app.py tests/
python -m pytest -v --cov=aceest
```

## Running with Docker

```bash
docker build -t aceest-fitness:local .
docker run -d -p 5000:5000 aceest-fitness:local
curl http://127.0.0.1:5000/health
```

## CI/CD Overview

**GitHub Actions** (`.github/workflows/main.yml`) runs on every push and
pull request against `main`: **Build & Lint** (compile check + flake8) ->
**Docker Image Assembly** -> **Automated Testing** (pytest run *inside*
the built container).

**Jenkins** (`Jenkinsfile`), running on the BITS Prayogshala lab VM, polls
GitHub every 5 minutes and runs: Checkout -> Setup Environment -> Lint ->
Unit Tests -> Docker Build. This is the BUILD and quality-gate stage
named in the assignment.

## Development History

Built as 12 feature branches (one per ACEest function), each merged via
its own pull request. A defect shipped with the report-export feature
(missing "client not found" handling, causing a 500 instead of a 404 for
an unknown client) was found after the next feature merged, and fixed via
`hotfix/report-404`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/auth/login` | Authenticate (seeded `admin`/`admin`) |
| POST | `/clients` | Create a client |
| GET | `/clients` | List clients |
| GET | `/clients/<n>` | Get one client |
| PUT | `/clients/<n>` | Update a client |
| GET | `/programs` | List available programs |
| GET | `/clients/<n>/bmi` | Calculate BMI and risk category |
| GET | `/clients/<n>/membership` | Check membership status |
| POST/GET | `/clients/<n>/workouts` | Log / list workouts |
| POST/GET | `/clients/<n>/metrics` | Log / list body metrics |
| GET | `/clients/<n>/metrics/weight-chart` | Weight-trend chart data |
| POST/GET | `/clients/<n>/progress` | Log / list weekly adherence |
| GET | `/clients/<n>/progress/chart` | Adherence chart data |
| GET | `/clients/<n>/summary` | Client summary dashboard |
| GET | `/clients/<n>/report.csv` | CSV client report |
| GET | `/clients/<n>/report.pdf` | PDF client report |
| POST | `/clients/<n>/program` | Assign a program template |
| POST | `/clients/<n>/ai-program` | Generate an experience-based plan |
| GET | `/analytics/overview` | Gym-wide analytics |
