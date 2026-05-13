# Local Development

Careero Layer 1 runs locally with a FastAPI backend and a React + Vite frontend.

## Backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Edit `backend/.env` so `CAREERO_DATABASE_URL` points at your local PostgreSQL database.

Health check:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

Run tests:

```powershell
pytest
```

## Frontend

From the repository root:

```powershell
cd frontend
npm install
npm run dev
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

Layer 1 is local-first only. It does not include authentication, tenants, workspaces, billing, cloud deployment, background job execution, database setup, or automated application submission.
