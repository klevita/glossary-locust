#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Locust Load Test Runner for Windows PowerShell

.DESCRIPTION
    Runs load tests for the Glossary application using Locust.
    Supports three test modes: normal, stress, and stability.

.PARAMETER Mode
    Test mode to run: normal, stress, or stability
    If not specified, launches Web UI

.PARAMETER UI
    Launch Web UI mode regardless of other parameters

.EXAMPLE
    .\run_test.ps1
    Launches Locust Web UI at http://localhost:8089

.EXAMPLE
    .\run_test.ps1 -Mode normal
    Runs normal workload test (5 minutes) in headless mode

.EXAMPLE
    .\run_test.ps1 -Mode stress
    Runs stress test (3 minutes) in headless mode

.EXAMPLE
    .\run_test.ps1 -Mode stability
    Runs stability test (10 minutes) in headless mode

.EXAMPLE
    .\run_test.ps1 -UI
    Launches Web UI mode
#>

param(
    [Parameter(Position=0)]
    [ValidateSet('normal', 'stress', 'stability', '')]
    [string]$Mode = '',

    [Parameter()]
    [switch]$UI
)

# Color output functions
function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

# Check if locust is installed
function Test-LocustInstalled {
    try {
        $null = Get-Command locust -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Main script
Write-Info "==================================================="
Write-Info "  Glossary Application - Locust Load Testing"
Write-Info "==================================================="
Write-Host ""

# Check if Locust is installed
if (-not (Test-LocustInstalled)) {
    Write-Warning "Locust is not installed!"
    Write-Host "Please run: pip install -r requirements.txt"
    exit 1
}

# Web UI mode
if ($UI -or $Mode -eq '') {
    Write-Info "Starting Locust Web UI..."
    Write-Success "Open http://localhost:8089 in your browser"
    Write-Host ""
    locust -f locustfile.py
    exit 0
}

# Headless mode with specific test scenario
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

switch ($Mode) {
    'normal' {
        Write-Info "Running Normal Workload Test..."
        Write-Host "  Duration: 5 minutes"
        Write-Host "  Peak Users: 80"
        Write-Host "  Pattern: Realistic daily usage"
        Write-Host ""

        $env:LOAD_TEST_MODE = "normal"
        $reportFile = "normal_workload_${timestamp}.html"

        locust -f locustfile.py --headless --html $reportFile

        if ($LASTEXITCODE -eq 0) {
            Write-Success "`nTest completed successfully!"
            Write-Success "Report saved to: $reportFile"
        }
    }

    'stress' {
        Write-Info "Running Stress Test..."
        Write-Host "  Duration: 3 minutes"
        Write-Host "  Peak Users: 800"
        Write-Host "  Pattern: Aggressive ramp-up to find limits"
        Write-Host ""

        $env:LOAD_TEST_MODE = "stress"
        $reportFile = "stress_test_${timestamp}.html"

        locust -f locustfile.py --headless --html $reportFile

        if ($LASTEXITCODE -eq 0) {
            Write-Success "`nTest completed successfully!"
            Write-Success "Report saved to: $reportFile"
        }
    }

    'stability' {
        Write-Info "Running Stability Test..."
        Write-Host "  Duration: 10 minutes"
        Write-Host "  Steady Users: 100"
        Write-Host "  Pattern: Long-duration constant load"
        Write-Host ""
        Write-Info "This test will run for 10 minutes."

        $env:LOAD_TEST_MODE = "stability"
        $reportFile = "stability_test_${timestamp}.html"
        $csvPrefix = "stability_${timestamp}"

        locust -f locustfile.py --headless --html $reportFile --csv $csvPrefix

        if ($LASTEXITCODE -eq 0) {
            Write-Success "`nTest completed successfully!"
            Write-Success "HTML Report: $reportFile"
            Write-Success "CSV Results: ${csvPrefix}_stats.csv, ${csvPrefix}_failures.csv"
        }
    }
}

Write-Host ""
Write-Info "==================================================="
