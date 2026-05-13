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
    & $python -m pytest tests/test_config.py tests/test_health.py

    Write-Host "Checking whether database-backed backend tests can run..."
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $dbCheck = & $python -c "from app.config import get_settings; from app.database import check_database; check_database(get_settings()); print('ok')" 2>$null
    $dbCheckExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($dbCheckExitCode -eq 0 -and $dbCheck -match "ok") {
        Write-Host "Database is reachable. Running database-backed backend tests..."
        & $python -m pytest tests/test_migrations.py tests/test_roles.py tests/test_role_api.py tests/test_database_health_integration.py
    }
    else {
        Write-Warning "Skipping database-backed backend tests because CAREERO_DATABASE_URL is not reachable. Fix PostgreSQL credentials, then rerun this script."
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
