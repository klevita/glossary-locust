# Load Testing Scenarios

This document describes the three load testing scenarios configured for the Glossary application.

## Overview

Three test scenarios are available:
1. **Normal Workload** - Realistic usage simulation
2. **Stress Test** - Performance limit identification
3. **Stability Test** - Long-duration degradation check

---

## 1. Normal Workload (Рабочая нагрузка)

**Purpose**: Simulate realistic daily usage patterns

**Duration**: 5 minutes

**Load Pattern**:
- 0-30s: Ramp up to 10 users (morning startup)
- 30s-1min: Ramp up to 50 users (business hours)
- 1-2.5min: Hold at 50 users (steady operation)
- 2.5-3min: Ramp up to 80 users (peak hour)
- 3-4min: Hold at 80 users (peak sustained)
- 4-4.5min: Ramp down to 30 users (afternoon lull)
- 4.5-5min: Hold at 30 users (end of day)

**Peak Users**: 80

### How to Run

**Option 1: Using environment variable**
```bash
# Windows CMD
set LOAD_TEST_MODE=normal
locust -f locustfile.py

# Windows PowerShell
$env:LOAD_TEST_MODE="normal"
locust -f locustfile.py

# Linux/Mac
LOAD_TEST_MODE=normal locust -f locustfile.py
```

**Option 2: Using command line**
```bash
locust -f locustfile.py NormalWorkloadShape
```

**Option 3: Web UI**
```bash
locust -f locustfile.py --web-host=0.0.0.0 --web-port=8089
# Open http://localhost:8089
# Select "NormalWorkloadShape" from the shape dropdown
# Click "Start"
```

---

## 2. Stress Test (Стресс-тест)

**Purpose**: Find performance limits and breaking points

**Duration**: 3 minutes

**Load Pattern**:
- 0-20s: Ramp up to 50 users rapidly
- 20-40s: Ramp up to 100 users
- 40s-1min: Ramp up to 200 users
- 1-1.5min: Ramp up to 500 users
- 1.5-2min: Hold at 500 users (observe system behavior)
- 2-2.5min: Spike to 800 users (find breaking point)
- 2.5-3min: Hold at 800 users (sustained peak)

**Peak Users**: 800

### How to Run

**Option 1: Using environment variable**
```bash
# Windows CMD
set LOAD_TEST_MODE=stress
locust -f locustfile.py

# Windows PowerShell
$env:LOAD_TEST_MODE="stress"
locust -f locustfile.py

# Linux/Mac
LOAD_TEST_MODE=stress locust -f locustfile.py
```

**Option 2: Using command line**
```bash
locust -f locustfile.py StressTestShape
```

### What to Monitor
- Response time degradation
- Error rate increases
- CPU and memory usage
- Database connection pool saturation
- Network bandwidth limits
- Server breaking point (when does it fail?)

---

## 3. Stability Test (Тест на стабильность)

**Purpose**: Check for degradation, memory leaks, and issues during prolonged operation

**Duration**: 10 minutes

**Load Pattern**:
- 0-1 min: Ramp up to 100 users (warmup)
- 1-9 min: Hold at 100 users (steady load)
- 9-10 min: Ramp down to 0 (graceful shutdown)

**Steady Users**: 100

### How to Run

**Option 1: Using environment variable**
```bash
# Windows CMD
set LOAD_TEST_MODE=stability
locust -f locustfile.py

# Windows PowerShell
$env:LOAD_TEST_MODE="stability"
locust -f locustfile.py

# Linux/Mac
LOAD_TEST_MODE=stability locust -f locustfile.py
```

**Option 2: Using command line**
```bash
locust -f locustfile.py StabilityTestShape
```

### What to Monitor
- **Memory leaks**: Check if memory usage grows continuously
- **Performance degradation**: Compare response times at 10min vs 60min
- **Connection pool exhaustion**: Database connections not being released
- **Resource cleanup**: Proper cleanup of gRPC channels, HTTP connections
- **Error accumulation**: Errors increasing over time

### Recommended Monitoring Tools
```bash
# Monitor server resources during test
# Memory usage
tasklist /FI "IMAGENAME eq python.exe" /FO LIST

# Or use Windows Performance Monitor
# Or install psutil and run:
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
```

---

## General Usage Tips

### Running Both REST and gRPC Tests

By default, Locust will run both `GlossaryRESTUser` and `GlossaryGRPCUser`. To specify:

```bash
# Run only REST tests
locust -f locustfile.py --user-classes GlossaryRESTUser StressTestShape

# Run only gRPC tests
locust -f locustfile.py --user-classes GlossaryGRPCUser StressTestShape

# Run both (default)
locust -f locustfile.py StressTestShape
```

### Headless Mode (No Web UI)

For CI/CD or automated testing:

```bash
# Normal workload - headless
LOAD_TEST_MODE=normal locust -f locustfile.py --headless

# Stress test - headless with HTML report
LOAD_TEST_MODE=stress locust -f locustfile.py --headless --html stress_report.html

# Stability test - headless with CSV output
LOAD_TEST_MODE=stability locust -f locustfile.py --headless --csv stability_results
```

### Distributed Load Testing

For generating more load across multiple machines:

```bash
# Master node
locust -f locustfile.py --master

# Worker nodes (run on other machines)
locust -f locustfile.py --worker --master-host=<master-ip>
```

---

## Test Results Interpretation

### Success Criteria

**Normal Workload**:
- 95th percentile response time < 200ms
- Error rate < 0.1%
- No timeouts

**Stress Test**:
- Identify maximum sustainable user count
- Document at what load errors begin
- Response time should degrade gracefully (not cliff-edge failure)

**Stability Test**:
- Response time variance < 10% over 1 hour
- No memory growth > 5% per hour
- Error rate remains constant (< 0.1%)
- No connection errors

### Common Issues to Look For

1. **Connection Pool Exhaustion**: Errors after sustained load
2. **Memory Leaks**: Increasing memory over time
3. **Database Locks**: Slow queries accumulating
4. **gRPC Channel Issues**: "Channel closed" errors
5. **Thread Pool Saturation**: Requests queuing up

---

## Troubleshooting

### Servers Not Running
Ensure both servers are running before testing:
- REST API: `http://localhost:8003`
- gRPC: `localhost:50051`

### Only Seeing One Protocol in Results
Check that both user classes are selected in the Web UI or via `--user-classes` parameter.

### Test Stops Early
Load shapes will automatically stop when duration is complete. This is expected behavior.

### High Error Rates
- Check server logs for errors
- Verify network connectivity
- Ensure servers have sufficient resources
- May need to reduce load (lower user counts)

---

## Customization

To modify test parameters, edit the `stages` arrays in `locustfile.py`:

```python
stages = [
    {"duration": 60, "users": 10, "spawn_rate": 1},  # seconds, target users, rate
    # Add more stages...
]
```

**Parameters**:
- `duration`: How long this stage lasts (seconds)
- `users`: Target number of concurrent users
- `spawn_rate`: How many users to add/remove per second
