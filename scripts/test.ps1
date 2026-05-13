Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$python = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Backend virtual environment not found. Create it before running tests."
}

Write-Host "Running backend unit tests..."
Push-Location $backendDir
try {
    & $python -m pytest tests/test_config.py tests/test_health.py tests/test_stride_rules.py tests/test_stride_prompt.py tests/test_stride_ai.py

    Write-Host "Checking whether database-backed backend tests can run..."
    if (-not $env:CAREERO_TEST_DATABASE_URL) {
        Write-Warning "Skipping database-backed backend tests because CAREERO_TEST_DATABASE_URL is not set."
    }
    else {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $dbCheck = & $python -c "import os; from sqlalchemy import create_engine, text; from app.database import sqlalchemy_url; engine = create_engine(sqlalchemy_url(os.environ['CAREERO_TEST_DATABASE_URL'])); connection = engine.connect(); connection.execute(text('SELECT 1')); connection.close(); engine.dispose(); print('ok')" 2>$null
        $dbCheckExitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorActionPreference
        if ($dbCheckExitCode -eq 0 -and $dbCheck -match "ok") {
            Write-Host "Test database is reachable. Running database-backed backend tests..."
            & $python -m pytest tests/test_migrations.py tests/test_roles.py tests/test_role_api.py tests/test_resume_sources_api.py tests/test_stride_evaluations.py tests/test_database_health_integration.py
        }
        else {
            Write-Warning "Skipping database-backed backend tests because CAREERO_TEST_DATABASE_URL is not reachable. Fix PostgreSQL credentials, then rerun this script."
        }
    }
}
finally {
    Pop-Location
}

Write-Host "Running frontend tests..."
Push-Location $frontendDir
try {
    & npm.cmd run test
    & npm.cmd run build
}
finally {
    Pop-Location
}
