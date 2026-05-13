# Scripts

Run these commands from the repository root in PowerShell.

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
.\scripts\migrate.ps1
.\scripts\seed.ps1
.\scripts\test.ps1
.\scripts\check-local.ps1
```

`check-local.ps1` verifies the backend, database health, frontend, and the frontend `/api` proxy. If PostgreSQL credentials are not configured correctly, database health and role API checks will fail until `backend/.env` points to reachable local databases.

If PowerShell blocks script execution, run a script with an explicit process-local bypass:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-local.ps1
```
