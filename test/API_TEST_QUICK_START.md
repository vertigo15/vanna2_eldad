# API Testing - Quick Start

## 🚀 Run in 3 Steps

### Step 1: Start Docker Container
```bash
docker-compose up -d
```

Wait for container to start (~10 seconds), then verify:
```bash
docker-compose ps
```

### Step 2: Run API Test
```bash
python test/test_api_questions.py
```

### Step 3: View Results
```bash
# View latest log (last 50 lines)
Get-Content test/logs/test_api_questions*.log -Tail 50 | Select -Last 50

# View JSON report
cat test/logs/test_api_questions_report.json | python -m json.tool
```

## What This Tests

**Posts each of 55 training questions to the live Vanna API and:**
1. ✅ Gets generated SQL back
2. ✅ Extracts SQL from response
3. ✅ Compares with expected SQL
4. ✅ Calculates similarity score

## Expected Output

```
Testing API Questions...

Test 1/55: What are the top 10 products by sales?
  Expected SQL: SELECT product_id, SUM(sales) FROM sales...
  Generated SQL: SELECT product_id, SUM(sales) FROM sales...
  Match: True (similarity: 100.0%)
  ✅ PASS

...

TEST SUMMARY
Total Tests: 55
Passed: 55
Failed: 0
Pass Rate: 100.0%
```

## Common Issues & Fixes

### ❌ Cannot connect to API
```bash
# Make sure container is running
docker-compose ps

# If not, start it
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### ❌ API request timeout
```bash
# Increase timeout in test_api_questions.py
API_TIMEOUT = 60  # was 30

# Or restart container
docker-compose restart
```

### ❌ "Could not extract SQL from response"
```bash
# Check Docker logs
docker-compose logs vanna-app --tail=50

# Test manually
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What tables exist?", "followup": false}'
```

## Integration with All Tests

### Run all 3 tests in sequence:
```bash
docker-compose up -d
python test/run_all_tests.py
```

This runs:
1. ✅ Validate Training Data (KB files)
2. ✅ Test All Questions (KB retrieval)
3. ✅ Test Questions via API (SQL generation)

### Each test produces:
- Console output
- Log file with timestamp
- JSON report with detailed results

## Typical Execution Time

- Start container: ~10 seconds
- Validate training: ~2 seconds
- Test KB questions: ~5 seconds
- **Test API (55 questions): ~2-5 minutes**

**Total: ~3-7 minutes** for all tests

## Test Report Location

After running, check:

```bash
test/logs/
├── test_api_questions_20250404_151025.log      # Full output
└── test_api_questions_report.json               # Structured results
```

## Advanced Options

### Run only API test (skip others)
```bash
python test/test_api_questions.py
```

### Run all tests
```bash
python test/run_all_tests.py
```

### Edit timeout (slow LLM)
```bash
# In test_api_questions.py, line 24
API_TIMEOUT = 60  # seconds
```

### Change API URL
```bash
# In test_api_questions.py, line 23
API_BASE_URL = "http://custom-host:8000"
```

## What Gets Tested

| Item | Count | Status |
|------|-------|--------|
| Training questions | 55 | ✅ All tested |
| API endpoint | 1 | ✅ /api/v1/chat |
| SQL extraction formats | 3 | ✅ All supported |
| Response timeout | - | ✅ 30 seconds |
| API health check | - | ✅ Verified |

## Metrics Tracked

For each question:
- ✅ Exact match (text comparison)
- ✅ Similarity score (keyword overlap)
- ✅ Pass/Fail status
- ✅ Error messages

## View Results

### Console (Real-time)
```bash
python test/test_api_questions.py
```

### Log File (Full history)
```bash
cat test/logs/test_api_questions_*.log
```

### JSON Report (Machine readable)
```bash
cat test/logs/test_api_questions_report.json | python -m json.tool
```

### Summary
```bash
# Extract summary from report
python -c "
import json
with open('test/logs/test_api_questions_report.json') as f:
    data = json.load(f)
    print(f\"Total: {data['total']}\")
    print(f\"Passed: {data['passed']}\")
    print(f\"Failed: {data['failed']}\")
    print(f\"Pass Rate: {data['pass_rate']:.1f}%\")
"
```

## Next: Check Results

1. **Quick check:**
   ```bash
   tail -20 test/logs/test_api_questions_*.log
   ```

2. **Detailed review:**
   ```bash
   cat test/logs/test_api_questions_report.json | python -m json.tool | less
   ```

3. **Failed tests only:**
   ```bash
   python -c "
   import json
   with open('test/logs/test_api_questions_report.json') as f:
       for r in json.load(f)['results']:
           if r['status'] != 'PASS':
               print(f\"Q{r['number']}: {r['question'][:60]}...\")
               print(f\"  Error: {r.get('error', 'N/A')}\")
   "
   ```

---

**For detailed information, see `API_TESTING.md`**
