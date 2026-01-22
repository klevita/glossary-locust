# Glossary Load Testing with Locust

This directory contains load testing configurations for the Glossary application, testing both REST API and gRPC endpoints.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Test Scenarios](#test-scenarios)
- [Understanding Results](#understanding-results)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.8 or higher
- pip (Python package manager)
- Running Glossary application servers:
  - **REST API**: `http://localhost:8003`
  - **gRPC Service**: `localhost:50051`

### Python Dependencies
```bash
pip install locust grpcio grpcio-tools
```

---

## Installation

### 1. Clone/Navigate to the Directory
```bash
cd C:\Users\kklev\dev\ITMO\glossary\locust
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install locust==2.20.0
pip install grpcio==1.60.0
pip install grpcio-tools==1.60.0
```

### 3. Verify Installation
```bash
locust --version
```

### 4. Generate gRPC Files (if needed)
If `glossary_pb2.py` or `glossary_pb2_grpc.py` are missing:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. glossary.proto
```

---

## Configuration

### File Structure
```
locust/
├── locustfile.py           # Main test file with user classes and load shapes
├── glossary.proto          # gRPC protocol definition
├── glossary_pb2.py         # Generated gRPC messages
├── glossary_pb2_grpc.py    # Generated gRPC service stubs
├── test_grpc.py            # gRPC connection test
├── TEST_SCENARIOS.md       # Detailed scenario documentation
└── README.md               # This file
```

### Server Endpoints

**REST API** (GlossaryRESTUser):
- Base URL: `http://localhost:8003`
- Endpoints:
  - `GET /glossary/getAll/` - Get all items
  - `PUT /glossary/update/{id}/` - Update item

**gRPC Service** (GlossaryGRPCUser):
- Address: `localhost:50051`
- Methods:
  - `GetAllItems` - Get all glossary items
  - `UpdateItem` - Update a glossary item

### User Classes

Both user classes will run by default, simulating mixed load:

- **GlossaryRESTUser**: Tests REST API endpoints (70% of requests are reads, 30% updates)
- **GlossaryGRPCUser**: Tests gRPC endpoints (70% of requests are reads, 30% updates)

---

## Running Tests

### Quick Start

#### 1. Web UI Mode (Recommended for beginners)
```bash
locust -f locustfile.py
```
Then open: `http://localhost:8089`

**Steps**:
1. Enter number of users
2. Enter spawn rate
3. Select load shape (optional): `NormalWorkloadShape`, `StressTestShape`, or `StabilityTestShape`
4. Click "Start"

#### 2. Using Environment Variable
```bash
# Windows PowerShell
$env:LOAD_TEST_MODE="normal"
locust -f locustfile.py

# Windows CMD
set LOAD_TEST_MODE=normal
locust -f locustfile.py

# Linux/Mac
LOAD_TEST_MODE=normal locust -f locustfile.py
```

**Available modes**: `normal`, `stress`, `stability`

#### 3. Directly Specify Load Shape
```bash
locust -f locustfile.py NormalWorkloadShape
```

### Headless Mode (No Web UI)

Best for CI/CD or automated testing:

```bash
# With HTML report
locust -f locustfile.py NormalWorkloadShape --headless --html report.html

# With CSV output
locust -f locustfile.py StressTestShape --headless --csv results

# Custom user count and duration
locust -f locustfile.py --headless -u 100 -r 10 -t 5m
```

**Parameters**:
- `-u, --users`: Number of concurrent users
- `-r, --spawn-rate`: Users to spawn per second
- `-t, --run-time`: Stop after specified time (e.g., 5m, 2h, 120s)
- `--html`: Generate HTML report
- `--csv`: Generate CSV files (results_stats.csv, results_failures.csv)

---

## Test Scenarios

### 1. Normal Workload Test
**Purpose**: Simulate realistic daily usage

```bash
# Environment variable method
$env:LOAD_TEST_MODE="normal"
locust -f locustfile.py

# Direct method
locust -f locustfile.py NormalWorkloadShape

# Headless with report
locust -f locustfile.py NormalWorkloadShape --headless --html normal_workload_report.html
```

**Configuration**:
- Duration: 5 minutes
- Peak users: 80
- Pattern: Gradual ramp-up mimicking business hours

**Expected Results**:
- 95th percentile response time < 200ms
- Error rate < 0.1%
- No timeouts

---

### 2. Stress Test
**Purpose**: Find performance limits

```bash
# Environment variable method
$env:LOAD_TEST_MODE="stress"
locust -f locustfile.py

# Direct method
locust -f locustfile.py StressTestShape

# Headless with report
locust -f locustfile.py StressTestShape --headless --html stress_test_report.html
```

**Configuration**:
- Duration: 3 minutes
- Peak users: 800
- Pattern: Aggressive ramp-up to breaking point

**What to Monitor**:
- At what user count do errors start?
- Response time degradation curve
- Server CPU/memory usage
- Database connection pool saturation

---

### 3. Stability Test
**Purpose**: Check for degradation and memory leaks

```bash
# Environment variable method
$env:LOAD_TEST_MODE="stability"
locust -f locustfile.py

# Direct method
locust -f locustfile.py StabilityTestShape

# Headless with CSV for analysis
locust -f locustfile.py StabilityTestShape --headless --csv stability_results
```

**Configuration**:
- Duration: 10 minutes
- Steady users: 100
- Pattern: Sustained constant load

**What to Monitor**:
- Memory growth over time (memory leaks)
- Response time at minute 2 vs minute 9
- Connection pool exhaustion
- Error rate stability

---

## Advanced Configurations

### Testing Specific Protocol Only

#### REST API Only
```bash
locust -f locustfile.py --user-classes GlossaryRESTUser NormalWorkloadShape
```

#### gRPC Only
```bash
locust -f locustfile.py --user-classes GlossaryGRPCUser StressTestShape
```

### Custom User Distribution

Create a custom ratio by modifying the command:

```bash
# 80% REST, 20% gRPC (not directly supported, use weight in code)
locust -f locustfile.py --user-classes GlossaryRESTUser GlossaryGRPCUser
```

To change task weights, modify the `@task()` decorator values in `locustfile.py`:
```python
@task(5)  # Higher number = more frequent
def get_all_items(self):
    ...

@task(1)  # Lower number = less frequent
def update_item(self):
    ...
```

### Distributed Load Testing

For generating load from multiple machines:

**Master Node**:
```bash
locust -f locustfile.py --master --master-bind-host=0.0.0.0 --master-bind-port=5557
```

**Worker Nodes** (on other machines):
```bash
locust -f locustfile.py --worker --master-host=<master-ip-address> --master-port=5557
```

### Custom Web UI Port
```bash
locust -f locustfile.py --web-host=0.0.0.0 --web-port=9090
```

---

## Understanding Results

### Locust Web UI

Access at `http://localhost:8089` to see:

1. **Statistics Tab**:
   - Request count
   - Failure rate
   - Response times (avg, min, max, median)
   - Requests per second (RPS)
   - Response size

2. **Charts Tab**:
   - Total requests per second
   - Response times over time
   - Number of users over time

3. **Failures Tab**:
   - Detailed error messages
   - Occurrence count

4. **Download Data**:
   - Click "Download Data" for CSV/Excel export

### Key Metrics to Analyze

#### Response Time
- **Median (50th percentile)**: Typical user experience
- **95th percentile**: Worst case for most users
- **Max**: Absolute worst case

**Good**: Median < 100ms, 95th < 200ms
**Warning**: Median < 500ms, 95th < 1000ms
**Critical**: Median > 500ms, 95th > 1000ms

#### Requests Per Second (RPS)
- Indicates system throughput
- Compare REST vs gRPC performance

#### Failure Rate
- **Good**: < 0.1%
- **Acceptable**: < 1%
- **Critical**: > 5%

### Sample Report Analysis

```
Type    Name                # reqs  # fails  Avg    Min   Max   Median  95%ile  99%ile  RPS
REST    REST: GetAll        5234    0        45     12    234   42      89      145     87.2
REST    REST: UpdateItem    1744    2        78     23    456   71      156     289     29.1
gRPC    gRPC: GetAllItems   5198    0        32     8     189   29      67      98      86.6
gRPC    gRPC: UpdateItem    1732    1        51     15    298   47      112     187     28.9
```

**Analysis**:
- gRPC is faster than REST (32ms vs 45ms for GetAll)
- Very low failure rate (0.05%)
- Response times are healthy (95th percentile < 200ms)
- System handles ~232 RPS total

---

## Monitoring Server Performance

### Windows

**Task Manager Method**:
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Performance" tab
3. Monitor CPU, Memory, Network during test

**PowerShell Method**:
```powershell
# Monitor process during test
while ($true) {
    Get-Process python | Select-Object Name, CPU, WorkingSet
    Start-Sleep -Seconds 5
}
```

### Linux/Mac

```bash
# Monitor CPU and Memory
top -p $(pgrep -f "your_server_process")

# Or use htop (more user-friendly)
htop

# Monitor specific Python process
watch -n 1 'ps aux | grep python'
```

### Database Monitoring

```bash
# PostgreSQL
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# MySQL
mysql -u root -p -e "SHOW PROCESSLIST;"
```

---

## Troubleshooting

### Issue: "Connection refused" errors

**Cause**: Servers not running

**Solution**:
```bash
# Verify REST API
curl http://localhost:8003/glossary/getAll/

# Verify gRPC (if you have grpcurl)
grpcurl -plaintext localhost:50051 list
```

Start your servers before running tests.

---

### Issue: Only seeing gRPC or only REST in results

**Cause**: Only one user class is being used

**Solution**:
```bash
# Ensure both user classes run (default behavior)
locust -f locustfile.py

# Or explicitly specify both
locust -f locustfile.py --user-classes GlossaryRESTUser GlossaryGRPCUser
```

---

### Issue: Load shape doesn't start

**Cause**: Load shape not recognized

**Solution**:
```bash
# Check exact class name (case-sensitive)
locust -f locustfile.py NormalWorkloadShape

# Or use environment variable
$env:LOAD_TEST_MODE="normal"
locust -f locustfile.py
```

---

### Issue: High failure rates (> 5%)

**Possible Causes**:
1. Server overwhelmed - reduce user count
2. Database connection pool exhausted - increase pool size
3. Network issues - check connectivity
4. Timeout too aggressive - increase timeout

**Solution**:
```bash
# Reduce load to find sustainable level
locust -f locustfile.py --headless -u 50 -r 5 -t 2m
```

Check server logs for specific errors.

---

### Issue: Import errors for glossary_pb2

**Cause**: gRPC files not generated

**Solution**:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. glossary.proto
```

---

### Issue: Test stops immediately

**Cause**: Load shape duration completed (expected behavior)

**Solution**: This is normal. Load shapes have defined durations:
- Normal: 5 minutes
- Stress: 3 minutes
- Stability: 10 minutes

Wait for completion or use manual mode without load shapes.

---

## Best Practices

### 1. Start Small
```bash
# Test with 10 users first
locust -f locustfile.py --headless -u 10 -r 2 -t 2m
```

### 2. Warm Up Servers
Run a small load test before your actual test to warm up caches, connection pools, etc.

### 3. Monitor Both Client and Server
- Watch Locust metrics (client-side)
- Monitor server CPU, memory, network
- Check database performance

### 4. Run Tests Multiple Times
- Results can vary
- Run 3 times and average results
- Check for consistency

### 5. Document Your Results
```bash
# Generate timestamped reports
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
locust -f locustfile.py StressTestShape --headless --html "report_$timestamp.html"
```

### 6. Use Version Control for Reports
```bash
# Create results directory
mkdir results
cd results

# Generate reports here
locust -f ../locustfile.py NormalWorkloadShape --headless --html normal_test.html
```

---

## Quick Reference Commands

```bash
# Basic web UI test
locust -f locustfile.py

# Normal workload (20 min)
$env:LOAD_TEST_MODE="normal"; locust -f locustfile.py

# Stress test (10 min)
$env:LOAD_TEST_MODE="stress"; locust -f locustfile.py

# Stability test (70 min)
$env:LOAD_TEST_MODE="stability"; locust -f locustfile.py

# Quick manual test (100 users, 5 min)
locust -f locustfile.py --headless -u 100 -r 10 -t 5m --html quick_test.html

# REST only
locust -f locustfile.py --user-classes GlossaryRESTUser

# gRPC only
locust -f locustfile.py --user-classes GlossaryGRPCUser

# Distributed (master)
locust -f locustfile.py --master

# Distributed (worker)
locust -f locustfile.py --worker --master-host=<master-ip>
```

---

## Additional Resources

- **Locust Documentation**: https://docs.locust.io/
- **gRPC Python**: https://grpc.io/docs/languages/python/
- **Test Scenarios Details**: See `TEST_SCENARIOS.md`

---

## Support

For issues specific to this test suite:
1. Check server logs
2. Verify both servers are running
3. Review `TEST_SCENARIOS.md` for detailed scenario information
4. Check Locust documentation for tool-specific questions

---

## License

This test suite is part of the Glossary application project.
