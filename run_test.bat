@echo off
REM Locust Load Test Runner for Windows
REM Usage: run_test.bat [normal|stress|stability]

setlocal

if "%1"=="" (
    echo Starting Locust Web UI...
    echo Open http://localhost:8089 in your browser
    locust -f locustfile.py
    goto :end
)

if "%1"=="normal" (
    echo Running Normal Workload Test (20 minutes)...
    set LOAD_TEST_MODE=normal
    locust -f locustfile.py --headless --html normal_workload_report.html
    goto :end
)

if "%1"=="stress" (
    echo Running Stress Test (10 minutes)...
    set LOAD_TEST_MODE=stress
    locust -f locustfile.py --headless --html stress_test_report.html
    goto :end
)

if "%1"=="stability" (
    echo Running Stability Test (70 minutes)...
    set LOAD_TEST_MODE=stability
    locust -f locustfile.py --headless --csv stability_results --html stability_test_report.html
    goto :end
)

echo Invalid argument: %1
echo Usage: run_test.bat [normal^|stress^|stability]
echo    Or run without arguments for Web UI mode

:end
endlocal
