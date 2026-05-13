# Local Development

Careero Layer 1 runs locally with a FastAPI backend and a React + Vite frontend.

## Backend

Create PostgreSQL databases for local development and tests:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Edit `backend/.env` so `CAREERO_DATABASE_URL` and `CAREERO_TEST_DATABASE_URL` point at your local PostgreSQL databases.
Run `python -m app.seed` after migrations so the default local user and canonical manual job sources are available for role intake.

Health check:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

Manual role intake API:

```text
POST   http://127.0.0.1:8000/api/roles
GET    http://127.0.0.1:8000/api/roles
GET    http://127.0.0.1:8000/api/roles/{role_id}
PATCH  http://127.0.0.1:8000/api/roles/{role_id}
DELETE http://127.0.0.1:8000/api/roles/{role_id}
```

LinkedIn roles are manually pasted into the API. Careero does not scrape LinkedIn or poll job boards in Layer 1.

Run tests:

```powershell
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

## Frontend

From the repository root:

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`, so start the backend first for role intake.

Manual role intake:

```text
http://127.0.0.1:5173/roles/new
```

Run frontend tests:

```powershell
npm run test
```

Build validation:

```powershell
npm run build
```

Preview a production build:

```powershell
npm run preview
```

If PowerShell blocks `npm.ps1`, run the same commands with `npm.cmd`, for example:

```powershell
npm.cmd install
npm.cmd run build
```

## Current Boundaries

Layer 1 is local-first only. It does not include authentication, tenants, workspaces, billing, cloud deployment, background job execution, or automated application submission.
