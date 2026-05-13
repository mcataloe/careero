# Backend

The backend is a local FastAPI application for Careero Layer 1.

Run from this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Run tests:

```powershell
pytest
```
