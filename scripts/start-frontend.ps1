Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$frontendDir = Join-Path $repoRoot "frontend"

Push-Location $frontendDir
try {
    & npm.cmd run dev
}
finally {
    Pop-Location
}
