# API Testing for Questions

## Overview

The `test_api_questions.py` script tests the Vanna 2.0 application by:
1. **Posting questions** to the live API running in Docker
2. **Extracting SQL** from the API response
3. **Comparing results** with expected SQL from training data
4. **Logging results** with detailed metrics

## Why This Test?

- **End-to-end validation** - Tests the complete pipeline (question → LLM → SQL)
- **Real API testing** - Validates actual Vanna Agent behavior
- **Training data verification** - Confirms if knowledge base helps generate correct SQL
- **Performance monitoring** - Measures API response times and reliability

## Prerequisites

### 1. Docker Container Must Be Running

```bash
# Start the container
docker-compose up -d

# Verify it's running
docker-compose ps

# Check health endpoint
curl http://localhost:8000/health
```

Should return status 200 with health info.

### 2. API Must Be Accessible

- URL: `http://localhost:8000`
- Port: 8000 (accessible)
- Health check: `GET /health`

### 3. Training Data Loaded

The API should have:
- Knowledge base with 55 questions
- Azure OpenAI LLM configured
- PostgreSQL database connection
- All training data in memory

## Running the Test

### Run Only API Test

```bash
python test/test_api_questions.py
```

### Run All Tests Including API

```bash
python test/run_all_tests.py
```

This will run:
1. Validate Training Data
2. Test All Questions (KB retrieval)
3. Test Questions via API (actual generation)

### Run with Specific Configuration

```bash
# Set API timeout to 60 seconds
$ENV:API_TIMEOUT = "60"
python test/test_api_questions.py
```

## Test Flow

```
┌─────────────────────────────────┐
│  Load 55 Training Questions     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Check API Connection           │
│  - GET /health                  │
│  - Verify status 200            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  For Each Question:             │
│  1. POST to API                 │
│  2. Extract SQL                 │
│  3. Compare with expected       │
│  4. Log result                  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Generate Report                │
│  - Console log                  │
│  - JSON report                  │
│  - Metrics & summary            │
└─────────────────────────────────┘
```

## Test Steps Explained

### Step 1: API Connection Check
```python
response = requests.get("http://localhost:8000/health", timeout=5)
```
- Verifies API is running
- Fails gracefully with clear error message if not

### Step 2: Load Training Questions
```python
questions = load_training_questions()  # 55 questions from training_data/queries.json
```

### Step 3: Post Question to API
```python
payload = {
    "question": "What are the top 10 products by sales?",
    "followup": False,
    "regenerate": False
}
response = requests.post("http://localhost:8000/api/v1/chat", json=payload)
```

### Step 4: Extract SQL from Response
The script handles multiple response formats:
- Direct `sql` field
- SQL in `message` wrapped in ` ```sql ` blocks
- Nested response structures

### Step 5: Compare SQL
```python
comparison = compare_sql(generated_sql, expected_sql)
```

Metrics:
- **exact_match** - Exact text match (normalized)
- **similarity** - Keyword overlap percentage
- **match** - Pass if similarity > 70% or exact match

## Response Extraction Examples

### Format 1: Direct SQL
```json
{
  "sql": "SELECT * FROM sales WHERE year = 2024"
}
```

### Format 2: SQL in Message
```json
{
  "message": "Here's the SQL:\n```sql\nSELECT * FROM sales\n```"
}
```

### Format 3: Nested Response
```json
{
  "response": {
    "sql": "SELECT * FROM sales"
  }
}
```

## Outputs

### Console Log
```
Test 1/55: What are the top 10 products by sales?
  Expected SQL: SELECT product_id, SUM(sales) FROM sales GROUP BY ...
  Generated SQL: SELECT product_id, SUM(sales) FROM sales GROUP BY ...
  Match: True (similarity: 100.0%)
  ✅ PASS
```

### File Outputs

#### Log File: `test/logs/test_api_questions_YYYYMMDD_HHMMSS.log`
- Full console output with timestamps
- Every test result
- API errors and exceptions
- Summary statistics

#### Report: `test/logs/test_api_questions_report.json`
```json
{
  "timestamp": "2025-04-11T15:10:28.707343",
  "api_url": "http://localhost:8000",
  "total": 55,
  "passed": 55,
  "failed": 0,
  "api_errors": 0,
  "pass_rate": 100.0,
  "results": [
    {
      "number": 1,
      "question": "What are the top 10 products?",
      "status": "PASS",
      "expected_sql": "...",
      "generated_sql": "...",
      "comparison": {
        "exact_match": true,
        "similarity": 1.0,
        "match": true
      }
    }
  ]
}
```

## Common Issues

### ❌ "Cannot connect to API"
**Cause:** Docker container not running
**Solution:**
```bash
docker-compose up -d
docker-compose ps  # Verify it's running
```

### ❌ "API request timeout"
**Cause:** API is slow or LLM service is slow
**Solution:**
```bash
# Increase timeout (edit test_api_questions.py)
API_TIMEOUT = 60  # was 30
```

### ❌ "Could not extract SQL from response"
**Cause:** Response format not recognized
**Solution:**
1. Check Docker logs: `docker-compose logs vanna-app`
2. Verify Vanna 2.0 version matches expected API format
3. Update `extract_sql_from_response()` for new format

### ❌ "No SQL in response"
**Cause:** API returned empty/invalid response
**Solution:**
1. Check if all training data is loaded
2. Check if Azure OpenAI is configured correctly
3. Check Docker container logs for errors

## Expected Results

### Best Case (100% Pass Rate)
```
Total Tests: 55
Passed: 55
Failed: 0
API Errors: 0
Pass Rate: 100.0%
```

### Normal Case (High Pass Rate)
```
Total Tests: 55
Passed: 50
Failed: 5
API Errors: 0
Pass Rate: 90.9%
```
- Some questions may generate different but valid SQL
- Counted as PASS_DIFFERENT

### Problem Case
```
Total Tests: 55
Passed: 10
Failed: 45
API Errors: 35
```
- Check Docker logs for API errors
- Verify Azure OpenAI connection
- Check PostgreSQL connection

## Troubleshooting

### View Docker Logs
```bash
docker-compose logs vanna-app --tail=100
```

### Check API Manually
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with a simple question
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What tables exist?", "followup": false}'
```

### View Test Report
```bash
# Pretty-print JSON report
cat test/logs/test_api_questions_report.json | python -m json.tool | head -50
```

## Configuration

Edit `test_api_questions.py` to customize:

```python
# Change API URL
API_BASE_URL = "http://localhost:8000"

# Change timeout (in seconds)
API_TIMEOUT = 30

# Change endpoint (if different version)
f"{API_BASE_URL}/api/v1/chat"
```

## Next Steps

1. **First run:** Verify the test works with Docker running
   ```bash
   python test/test_api_questions.py
   ```

2. **Check results:** Review the JSON report
   ```bash
   cat test/logs/test_api_questions_report.json | python -m json.tool
   ```

3. **Iterate:** Update training data or API if needed
   ```bash
   # Update training data
   # Restart container
   docker-compose restart
   
   # Re-run tests
   python test/test_api_questions.py
   ```

## Integration with CI/CD

This test can be added to CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run API tests
  run: |
    docker-compose up -d
    python test/test_api_questions.py
    docker-compose down
```

Exit codes:
- `0` - All tests passed
- `1` - One or more tests failed

## Performance Metrics

Typical execution times:
- API connection check: ~1 second
- Per question: ~2-5 seconds (depends on LLM)
- 55 questions total: ~2-5 minutes
- Report generation: <1 second

Total: **2-10 minutes** depending on:
- Azure OpenAI response time
- Network latency
- Docker container performance
- System load
