# Backend

The backend is a local FastAPI application for Careero Layer 1.

## Setup

Run from this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `.env` for your local machine. The default values are:

```dotenv
CAREERO_APP_NAME=Careero API
CAREERO_ENVIRONMENT=local
CAREERO_DATABASE_URL=postgresql://careero:careero@localhost:5432/careero
CAREERO_OPENAI_API_KEY=
CAREERO_LOG_LEVEL=INFO
```

`CAREERO_OPENAI_API_KEY` is intentionally empty in local setup. Do not commit real secrets.

## Run

```powershell
uvicorn app.main:app --reload
```

Health checks:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

`/health/database` connects to the PostgreSQL database configured by `CAREERO_DATABASE_URL` and runs a lightweight probe.

## Test

Run tests:

```powershell
pytest
```
