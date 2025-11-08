# Control script for generator container lifecycle management (PowerShell)

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('pause', 'resume', 'status')]
    [string]$Command
)

$ContainerName = "generator"

function Show-Usage {
    Write-Host @"
Usage: .\control-generator.ps1 {pause|resume|status}

Commands:
    pause   - Pause generation (send SIGUSR1)
    resume  - Resume generation (send SIGUSR2)
    status  - Show current generation status

Examples:
    .\control-generator.ps1 pause
    .\control-generator.ps1 resume
    .\control-generator.ps1 status
"@
}

function Test-ContainerRunning {
    $running = docker ps --format '{{.Names}}' | Where-Object { $_ -eq $ContainerName }
    if (-not $running) {
        Write-Host "ERROR: Container '$ContainerName' is not running" -ForegroundColor Red
        Write-Host "Start it with: cd docker && docker compose up -d"
        exit 1
    }
}

function Invoke-Pause {
    Test-ContainerRunning
    Write-Host "Pausing generator..." -ForegroundColor Yellow
    docker exec $ContainerName kill -SIGUSR1 1
    Write-Host "✓ Pause signal sent (SIGUSR1)" -ForegroundColor Green
    Write-Host "Generation will pause after completing current batch"
}

function Invoke-Resume {
    Test-ContainerRunning
    Write-Host "Resuming generator..." -ForegroundColor Yellow
    docker exec $ContainerName kill -SIGUSR2 1
    Write-Host "✓ Resume signal sent (SIGUSR2)" -ForegroundColor Green
    Write-Host "Generation will resume from next scheduled interval"
}

function Show-Status {
    Test-ContainerRunning
    Write-Host "Generator container status:" -ForegroundColor Cyan
    Write-Host "----------------------------------------"
    docker ps --filter "name=$ContainerName" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"
    Write-Host ""
    Write-Host "Recent logs:" -ForegroundColor Cyan
    Write-Host "----------------------------------------"
    $logs = docker logs --tail 10 $ContainerName 2>&1
    $filtered = $logs | Select-String -Pattern "(PAUSE|RESUME|batch generated|Starting)"
    if ($filtered) {
        $filtered
    } else {
        Write-Host "No recent activity"
    }
    Write-Host ""
    Write-Host "State file (if exists):" -ForegroundColor Cyan
    Write-Host "----------------------------------------"
    $stateFile = docker exec $ContainerName cat /data/manifests/generator_state.json 2>$null
    if ($stateFile) {
        $stateFile | ConvertFrom-Json | ConvertTo-Json -Depth 10
    } else {
        Write-Host "No state file yet"
    }
}

# Main
switch ($Command) {
    'pause' { Invoke-Pause }
    'resume' { Invoke-Resume }
    'status' { Show-Status }
    default {
        Show-Usage
        exit 1
    }
}
