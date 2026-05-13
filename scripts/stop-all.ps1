Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendPort = 8000
$frontendPort = 5173

function Get-ListeningProcessId {
    param([int]$Port)

    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique
}

function Get-ProcessCommandLine {
    param([int]$ProcessId)

    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return ""
    }

    return [string]$process.CommandLine
}

function Test-CareeroProcess {
    param([int]$ProcessId)

    $currentProcessId = $ProcessId
    for ($depth = 0; $depth -lt 6 -and $currentProcessId -gt 0; $depth++) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $currentProcessId" -ErrorAction SilentlyContinue
        if ($null -eq $process) {
            return $false
        }

        $commandLine = [string]$process.CommandLine
        if (
            ($commandLine -like "*$repoRoot*scripts\start-backend.ps1*") -or
            ($commandLine -like "*$repoRoot*scripts\start-frontend.ps1*") -or
            ($commandLine -like "*$repoRoot*backend*" -and $commandLine -like "*uvicorn app.main:app --reload*") -or
            ($commandLine -like "*$repoRoot*frontend*" -and $commandLine -like "*vite*")
        ) {
            return $true
        }

        $currentProcessId = [int]$process.ParentProcessId
    }

    return $false
}

function Stop-CareeroProcess {
    param(
        [int]$ProcessId,
        [string]$Reason
    )

    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return
    }

    Write-Host "Stopping PID $ProcessId ($($process.ProcessName)) - $Reason"
    Stop-Process -Id $ProcessId -Force
}

function Get-CareeroCandidateIds {
    $candidateIds = New-Object System.Collections.Generic.HashSet[int]

    foreach ($port in @($backendPort, $frontendPort)) {
        foreach ($processId in @(Get-ListeningProcessId -Port $port)) {
            [void]$candidateIds.Add([int]$processId)
            $childProcesses = Get-CimInstance Win32_Process |
                Where-Object {
                    $_.ParentProcessId -eq $processId -or
                    ([string]$_.CommandLine -like "*parent_pid=$processId*")
                }

            foreach ($childProcess in $childProcesses) {
                [void]$candidateIds.Add([int]$childProcess.ProcessId)
            }
        }
    }

    $careeroProcesses = Get-CimInstance Win32_Process |
        Where-Object {
            $commandLine = [string]$_.CommandLine
            $commandLine -and
            (
                ($commandLine -like "*$repoRoot*scripts\start-backend.ps1*") -or
                ($commandLine -like "*$repoRoot*scripts\start-frontend.ps1*") -or
                ($commandLine -like "*$repoRoot*backend*" -and $commandLine -like "*uvicorn app.main:app --reload*") -or
                ($commandLine -like "*$repoRoot*frontend*" -and $commandLine -like "*vite*")
            )
        }

    foreach ($process in $careeroProcesses) {
        [void]$candidateIds.Add([int]$process.ProcessId)
    }

    return $candidateIds
}

$stoppedAny = $false
for ($pass = 1; $pass -le 6; $pass++) {
    $candidateIds = @(Get-CareeroCandidateIds)
    if ($candidateIds.Count -eq 0) {
        break
    }

    foreach ($processId in $candidateIds) {
        $commandLine = Get-ProcessCommandLine -ProcessId $processId
        $isBackendWorkerForKnownListener =
            $commandLine -like "*multiprocessing.spawn*" -and
            $commandLine -like "*--multiprocessing-fork*"

        if ((Test-CareeroProcess -ProcessId $processId) -or $isBackendWorkerForKnownListener) {
            Stop-CareeroProcess -ProcessId $processId -Reason "Careero dev service"
            $stoppedAny = $true
        }
        elseif ($commandLine) {
            Write-Warning "Skipping PID $processId because it does not look like a Careero dev process."
            Write-Warning "Command line: $commandLine"
        }
    }

    Start-Sleep -Seconds 1
}

if (-not $stoppedAny) {
    Write-Host "No Careero backend/frontend dev processes found."
}

Write-Host ""
Write-Host "Remaining Careero listeners:"
$remaining = Get-NetTCPConnection -LocalPort $backendPort, $frontendPort -State Listen -ErrorAction SilentlyContinue
if ($remaining) {
    $remaining | Select-Object LocalAddress, LocalPort, State, OwningProcess | Format-Table -AutoSize
}
else {
    Write-Host "None."
}
