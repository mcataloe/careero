# Frontend

The frontend is a local React + Vite + TypeScript application for Careero Layer 1. It uses Mantine for UI components and talks to the backend through the Vite `/api` proxy.

Run from this directory:

```powershell
npm install
npm run dev
```

The frontend expects the backend at:

```text
http://127.0.0.1:8000
```

Before using role intake, run the backend database setup:

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Manual role intake is available at:

```text
http://127.0.0.1:5173/roles/new
```

Run component tests:

```powershell
npm run test
```

Build validation:

```powershell
npm run build
```

If PowerShell blocks `npm`, use `npm.cmd`.
