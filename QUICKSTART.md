# Quick Start Guide

Get up and running with load tests in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] REST API server running on `http://localhost:8003`
- [ ] gRPC server running on `localhost:50051`

## Installation (One-Time Setup)

```bash
# Install dependencies
pip install -r requirements.txt
```

That's it! You're ready to test.

---

## Run Your First Test

### Option 1: Web UI (Easiest)

**Windows PowerShell:**
```powershell
.\run_test.ps1
```

**Windows CMD:**
```cmd
run_test.bat
```

**Linux/Mac:**
```bash
./run_test.sh
```

Then open: **http://localhost:8089**

Click "Start" and watch your tests run!

---

### Option 2: Automated Tests (Recommended)

#### Normal Workload Test (5 minutes)
```powershell
# PowerShell
.\run_test.ps1 -Mode normal

# CMD
run_test.bat normal

# Linux/Mac
./run_test.sh normal
```

#### Stress Test (3 minutes)
```powershell
# PowerShell
.\run_test.ps1 -Mode stress

# CMD
run_test.bat stress

# Linux/Mac
./run_test.sh stress
```

#### Stability Test (10 minutes)
```powershell
# PowerShell
.\run_test.ps1 -Mode stability

# CMD
run_test.bat stability

# Linux/Mac
./run_test.sh stability
```

---

## Understanding Your Results

After the test completes, open the HTML report:
- `normal_workload_YYYYMMDD_HHMMSS.html`
- `stress_test_YYYYMMDD_HHMMSS.html`
- `stability_test_YYYYMMDD_HHMMSS.html`

### What to Look For

**Response Time**:
- ✅ Good: Median < 100ms, 95th percentile < 200ms
- ⚠️ Warning: Median < 500ms, 95th percentile < 1000ms
- ❌ Bad: Median > 500ms

**Failure Rate**:
- ✅ Good: < 0.1%
- ⚠️ Warning: < 1%
- ❌ Bad: > 5%

**Requests Per Second (RPS)**:
- Higher is better
- Compare REST vs gRPC performance

---

## Troubleshooting

### "Connection refused" error
**Problem:** Servers not running

**Fix:**
```bash
# Check REST API
curl http://localhost:8003/glossary/getAll/

# If it fails, start your REST server first
```

### "Module not found" error
**Problem:** Dependencies not installed

**Fix:**
```bash
pip install -r requirements.txt
```

### Only seeing gRPC or only REST
**Problem:** Only one protocol being tested

**Fix:** Make sure both servers are running, then restart the test

---

## Next Steps

Once you've run your first test:

1. **Read the full README** for advanced configurations
2. **Check TEST_SCENARIOS.md** for detailed scenario explanations
3. **Customize** the test parameters in `locustfile.py`
4. **Monitor** your servers during tests

---

## Quick Reference

```bash
# Web UI mode
.\run_test.ps1                    # PowerShell
run_test.bat                      # CMD
./run_test.sh                     # Linux/Mac

# Normal workload (5 min)
.\run_test.ps1 -Mode normal       # PowerShell
run_test.bat normal               # CMD
./run_test.sh normal              # Linux/Mac

# Stress test (3 min)
.\run_test.ps1 -Mode stress       # PowerShell
run_test.bat stress               # CMD
./run_test.sh stress              # Linux/Mac

# Stability test (10 min)
.\run_test.ps1 -Mode stability    # PowerShell
run_test.bat stability            # CMD
./run_test.sh stability           # Linux/Mac
```

---

**Need more help?** See [README.md](README.md) for comprehensive documentation.
