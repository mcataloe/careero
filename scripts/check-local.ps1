Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Check {
    param(
        [string] $Name,
        [string] $Uri,
        [int[]] $AllowedStatusCodes = @(200)
    )

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 5
        if ($AllowedStatusCodes -notcontains [int]$response.StatusCode) {
            throw "Expected $($AllowedStatusCodes -join ', '), got $($response.StatusCode)"
        }
        Write-Host "[OK] $Name -> $($response.StatusCode)"
        return $true
    }
    catch {
        Write-Warning "[FAIL] $Name -> $($_.Exception.Message)"
        return $false
    }
}

$allOk = $true
$allOk = (Invoke-Check -Name "Backend health" -Uri "http://127.0.0.1:8000/health") -and $allOk
$allOk = (Invoke-Check -Name "Database health" -Uri "http://127.0.0.1:8000/health/database") -and $allOk
$allOk = (Invoke-Check -Name "Frontend" -Uri "http://127.0.0.1:5173/roles/new") -and $allOk
$allOk = (Invoke-Check -Name "Frontend API proxy roles" -Uri "http://127.0.0.1:5173/api/roles") -and $allOk

if (-not $allOk) {
    Write-Host ""
    Write-Host "Local readiness failed."
    Write-Host "Common fix: create/fix the local PostgreSQL role and databases, update backend/.env, then run:"
    Write-Host "  .\scripts\migrate.ps1"
    Write-Host "  .\scripts\seed.ps1"
    exit 1
}

Write-Host "Local Careero services are ready."
