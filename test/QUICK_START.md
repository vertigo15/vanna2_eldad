# Test Suite - Quick Reference

## Run All Tests
```bash
python test/run_all_tests.py
```

## Run Individual Tests

**Validate Training Data:**
```bash
python test/validate_training.py
```

**Test All Questions:**
```bash
python test/test_all_questions.py
```

## View Results

**Latest Logs:**
```bash
# View last 50 lines of latest log
Get-Content (Get-ChildItem test/logs/*.log | Sort-Object LastWriteTime -Desc | Select-Object -First 1).FullName -Tail 50
```

**View JSON Reports:**
```bash
# Validate training report
cat test/logs/validate_training_report.json | python -m json.tool

# Test results report
cat test/logs/test_all_questions_report.json | python -m json.tool

# Suite summary report
cat test/logs/run_all_tests_report.json | python -m json.tool
```

## Log Locations
```
test/logs/
├── validate_training_YYYYMMDD_HHMMSS.log
├── validate_training_report.json
├── test_all_questions_YYYYMMDD_HHMMSS.log
├── test_all_questions_report.json
├── run_all_tests_YYYYMMDD_HHMMSS.log
└── run_all_tests_report.json
```

## Expected Results

✅ All tests should pass with 100% pass rate:
- Validate Training Data: 3/3 checks
- Test All Questions: 55/55 questions found

## Exit Codes
- `0` - All tests passed ✅
- `1` - One or more tests failed ❌

## Troubleshooting

**Tests fail to run:**
1. Check Docker container: `docker-compose ps`
2. Verify training data exists: `ls training_data/`
3. Check .env file is present

**Import errors:**
1. Verify you're in the project root directory
2. Check PYTHONPATH includes current directory
3. Run tests as: `python test/run_all_tests.py`

**Encoding errors:**
1. These are usually non-fatal (console encoding on Windows)
2. Check log files (UTF-8 encoded) for actual results
3. JSON reports should always be valid

## Test Descriptions

### validate_training.py
Checks:
- ✅ All JSON files exist and are valid
- ✅ Knowledge base loads successfully
- ✅ Schema structure is complete

Files checked:
- schema.json (35 tables)
- queries.json (55 question-SQL pairs)
- documentation.json (53 terms, 7 rules)
- sql_patterns.json (14 patterns)
- samples.json (16 sample tables)

### test_all_questions.py
Checks:
- ✅ All 55 training questions exist in knowledge base
- ✅ Questions can be retrieved and matched
- ✅ Associated SQL queries are available

## Quick Commands

**Run suite and check pass/fail:**
```bash
python test/run_all_tests.py; echo "Exit code: $?"
```

**Run tests with silent console output (logs only):**
```bash
python test/run_all_tests.py 2>nul 1>nul
```

**Check test status without running:**
```bash
# Check if logs directory exists
Test-Path test/logs

# List recent test reports
Get-ChildItem test/logs/*.json | Sort-Object LastWriteTime -Desc | Select-Object -First 3
```

## Docker Integration

**Run tests in Docker container:**
```bash
docker-compose exec vanna-app python test/run_all_tests.py
```

**Run specific test in Docker:**
```bash
docker-compose exec vanna-app python test/validate_training.py
```

**Check Docker container health:**
```bash
docker-compose ps
```

## Performance

Typical execution times:
- validate_training.py: ~2-3 seconds
- test_all_questions.py: ~5-10 seconds
- run_all_tests.py: ~10-15 seconds total

If tests run significantly slower, check:
1. Docker container resources
2. Database connection latency
3. System load

## Adding Tests

1. Create new file in `test/` folder: `test_my_feature.py`
2. Import utilities:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   from conftest import setup_logger, save_json_report
   ```
3. Setup logging:
   ```python
   logger, log_path = setup_logger("my_test", "my_test.log")
   ```
4. Create main test function and report
5. Add to `run_all_tests.py` TESTS list:
   ```python
   TESTS = [
       ("validate_training.py", "Validate Training Data"),
       ("test_all_questions.py", "Test All Questions"),
       ("test_my_feature.py", "My Feature Test"),  # ← Add here
   ]
   ```

## Next Run

```bash
cd C:\Users\user\OneDrive - JeenAI\Documents\code\vanna2_eldad
python test/run_all_tests.py
```
