# Backend

The backend is a local FastAPI application for Careero Layer 1.

## PostgreSQL

Create local development and test databases before running migrations. One simple local setup is:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

If PostgreSQL is installed on Windows but `psql` is not on your `PATH`, run it from the PostgreSQL `bin` directory for your installed version.

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
CAREERO_TEST_DATABASE_URL=postgresql://careero:careero@localhost:5432/careero_test
CAREERO_OPENAI_API_KEY=
CAREERO_LOG_LEVEL=INFO
```

`CAREERO_OPENAI_API_KEY` is intentionally empty in local setup. Do not commit real secrets.

## Migrate and Seed

Run migrations:

```powershell
python -m alembic upgrade head
```

Seed the default local user:

```powershell
python -m app.seed
```

The seed command is idempotent. It creates or updates `local-user@careero.local`.

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
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

Database-backed tests run Alembic migrations against `CAREERO_TEST_DATABASE_URL` and reset the known Careero schema in that test database.
