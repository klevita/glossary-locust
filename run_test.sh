#!/bin/bash
# Locust Load Test Runner for Linux/Mac
# Usage: ./run_test.sh [normal|stress|stability]

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if locust is installed
check_locust() {
    if ! command -v locust &> /dev/null; then
        print_error "Locust is not installed!"
        echo "Please run: pip install -r requirements.txt"
        exit 1
    fi
}

# Header
print_info "==================================================="
print_info "  Glossary Application - Locust Load Testing"
print_info "==================================================="
echo ""

check_locust

# Web UI mode (no arguments)
if [ $# -eq 0 ]; then
    print_info "Starting Locust Web UI..."
    print_success "Open http://localhost:8089 in your browser"
    echo ""
    locust -f locustfile.py
    exit 0
fi

# Headless mode with specific test scenario
MODE=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

case $MODE in
    normal)
        print_info "Running Normal Workload Test..."
        echo "  Duration: 5 minutes"
        echo "  Peak Users: 80"
        echo "  Pattern: Realistic daily usage"
        echo ""

        export LOAD_TEST_MODE=normal
        REPORT_FILE="normal_workload_${TIMESTAMP}.html"

        locust -f locustfile.py --headless --html "$REPORT_FILE"

        if [ $? -eq 0 ]; then
            echo ""
            print_success "Test completed successfully!"
            print_success "Report saved to: $REPORT_FILE"
        fi
        ;;

    stress)
        print_info "Running Stress Test..."
        echo "  Duration: 3 minutes"
        echo "  Peak Users: 800"
        echo "  Pattern: Aggressive ramp-up to find limits"
        echo ""

        export LOAD_TEST_MODE=stress
        REPORT_FILE="stress_test_${TIMESTAMP}.html"

        locust -f locustfile.py --headless --html "$REPORT_FILE"

        if [ $? -eq 0 ]; then
            echo ""
            print_success "Test completed successfully!"
            print_success "Report saved to: $REPORT_FILE"
        fi
        ;;

    stability)
        print_info "Running Stability Test..."
        echo "  Duration: 10 minutes"
        echo "  Steady Users: 100"
        echo "  Pattern: Long-duration constant load"
        echo ""
        print_info "This test will run for 10 minutes."

        export LOAD_TEST_MODE=stability
        REPORT_FILE="stability_test_${TIMESTAMP}.html"
        CSV_PREFIX="stability_${TIMESTAMP}"

        locust -f locustfile.py --headless --html "$REPORT_FILE" --csv "$CSV_PREFIX"

        if [ $? -eq 0 ]; then
            echo ""
            print_success "Test completed successfully!"
            print_success "HTML Report: $REPORT_FILE"
            print_success "CSV Results: ${CSV_PREFIX}_stats.csv, ${CSV_PREFIX}_failures.csv"
        fi
        ;;

    *)
        print_error "Invalid argument: $MODE"
        echo "Usage: $0 [normal|stress|stability]"
        echo "   Or run without arguments for Web UI mode"
        exit 1
        ;;
esac

echo ""
print_info "==================================================="
