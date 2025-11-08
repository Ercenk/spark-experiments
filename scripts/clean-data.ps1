#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Clean all generated data files and start fresh.

.DESCRIPTION
    This script removes all JSON batches from data/raw/ and data/manifests/,
    preserving the directory structure. Useful for starting a new experiment
    or resetting the simulation state.

.PARAMETER Confirm
    Skip confirmation prompt and proceed with cleanup.

.EXAMPLE
    .\scripts\clean-data.ps1
    Interactive mode with confirmation prompt.

.EXAMPLE
    .\scripts\clean-data.ps1 -Confirm
    Skip confirmation and proceed directly with cleanup.

.NOTES
    The generator container must be restarted after cleanup to reinitialize.
#>

param(
    [switch]$Confirm
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $PSCommandPath
$RootDir = Split-Path -Parent $ScriptDir

# Build Python command
$PythonScript = Join-Path $RootDir "scripts\clean-data.py"

if (-not (Test-Path $PythonScript)) {
    Write-Error "Python script not found: $PythonScript"
    exit 1
}

# Build arguments
$args = @($PythonScript)
if ($Confirm) {
    $args += "--confirm"
}

# Execute Python script
try {
    & python $args
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "To restart with clean data:" -ForegroundColor Cyan
        Write-Host "  cd docker" -ForegroundColor Gray
        Write-Host "  docker compose restart generator" -ForegroundColor Gray
    }
    
    exit $exitCode
}
catch {
    Write-Error "Failed to execute cleanup script: $_"
    exit 1
}
