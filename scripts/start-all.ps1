Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendPort = 8000
$frontendPort = 5173

function Get-ListeningProcessId {
    param([int]$Port)

    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1

    if ($null -eq $connection) {
        return $null
    }

    return $connection.OwningProcess
}

function Get-ProcessCommandLine {
    param([int]$ProcessId)

    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return ""
    }

    return [string]$process.CommandLine
}

function Test-CareeroProcessTree {
    param(
        [int]$ProcessId,
        [string]$ExpectedCommandFragment
    )

    $currentProcessId = $ProcessId
    for ($depth = 0; $depth -lt 6 -and $currentProcessId -gt 0; $depth++) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $currentProcessId" -ErrorAction SilentlyContinue
        if ($null -eq $process) {
            return $false
        }

        $commandLine = [string]$process.CommandLine
        if ($commandLine -like "*$ExpectedCommandFragment*" -or $commandLine -like "*$repoRoot*") {
            return $true
        }

        $currentProcessId = [int]$process.ParentProcessId
    }

    return $false
}

function Start-CareeroService {
    param(
        [string]$Name,
        [int]$Port,
        [string]$ScriptPath,
        [string]$ExpectedCommandFragment
    )

    $existingPid = Get-ListeningProcessId -Port $Port
    if ($null -ne $existingPid) {
        $commandLine = Get-ProcessCommandLine -ProcessId $existingPid
        if (Test-CareeroProcessTree -ProcessId $existingPid -ExpectedCommandFragment $ExpectedCommandFragment) {
            Write-Host "$Name already running on port $Port (PID $existingPid)."
            return
        }

        Write-Warning "$Name was not started because port $Port already has a listener owned by PID $existingPid."
        if ($commandLine) {
            Write-Warning "Command line: $commandLine"
        }
        return
    }

    Write-Host "Starting $Name on port $Port..."
    Start-Process powershell.exe `
        -WindowStyle Hidden `
        -WorkingDirectory $repoRoot `
        -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $ScriptPath
}

$backendScript = Join-Path $PSScriptRoot "start-backend.ps1"
$frontendScript = Join-Path $PSScriptRoot "start-frontend.ps1"

Start-CareeroService `
    -Name "Careero backend" `
    -Port $backendPort `
    -ScriptPath $backendScript `
    -ExpectedCommandFragment "uvicorn app.main:app --reload"

Start-CareeroService `
    -Name "Careero frontend" `
    -Port $frontendPort `
    -ScriptPath $frontendScript `
    -ExpectedCommandFragment "vite"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Current listeners:"
Get-NetTCPConnection -LocalPort $backendPort, $frontendPort -State Listen -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, State, OwningProcess |
    Format-Table -AutoSize

Write-Host "Backend:  http://127.0.0.1:$backendPort"
Write-Host "Frontend: http://localhost:$frontendPort"
