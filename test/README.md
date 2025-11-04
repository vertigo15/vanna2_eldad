# Test Suite for Vanna 2.0

This folder contains all tests and validation scripts for the Vanna 2.0 training data system.

## Quick Start

Run all tests with unified logging:
```bash
python test/run_all_tests.py
```

Or run individual tests:
```bash
python test/validate_training.py    # Validate training data files
python test/test_all_questions.py   # Test all 55 training questions
```

## Test Files

### `conftest.py`
Centralized test configuration and utilities:
- `setup_logger(name, suffix)` - Creates logger with file and console output
- `save_json_report(data, filename)` - Saves structured test results as JSON
- `load_training_questions()` - Loads all training questions from training_data/queries.json

All logs are written to `test/logs/` directory with timestamp-based filenames.

### `run_all_tests.py`
Master test runner that orchestrates all tests with:
- Unified logging via `conftest.py`
- Sequential test execution
- Pass/fail tracking
- JSON report generation in `test/logs/`

**Usage:**
```bash
python test/run_all_tests.py
```

### `validate_training.py`
Validates training data files and knowledge base:
- **Step 1**: Validate all JSON training files exist and are valid
- **Step 2**: Validate knowledge base loads successfully
- **Step 3**: Validate schema structure

**Checks:**
- ✅ Training Files: schema.json, queries.json, documentation.json, sql_patterns.json, samples.json
- ✅ Knowledge Base: Loads 55 examples, 53 business terms
- ✅ Schema Structure: All 35 tables have required fields

**Usage:**
```bash
python test/validate_training.py
```

**Output:**
- Console log with detailed validation steps
- `test/logs/validate_training_YYYYMMDD_HHMMSS.log`
- `test/logs/validate_training_report.json`

### `test_all_questions.py`
Tests if the knowledge base can generate SQL for all 55 training questions:
- Loads all questions from training_data/queries.json
- Calls `kb.generate_sql(question)` for each question
- Compares generated SQL with expected SQL
- Tracks pass/fail metrics

**Checks:**
- Exact SQL match
- SQL generation success (returns non-null)
- Exception handling

**Usage:**
```bash
python test/test_all_questions.py
```

**Output:**
- Console log with per-question results
- `test/logs/test_all_questions_YYYYMMDD_HHMMSS.log`
- `test/logs/test_all_questions_report.json`

### `test_api_questions.py`
End-to-end test: Posts all 55 training questions to the Vanna API and validates generated SQL:
- **Prerequisite:** Docker container must be running (`docker-compose up -d`)
- Posts each question to `/api/v1/chat` endpoint
- Extracts SQL from API response
- Compares with expected SQL from training data
- Validates response extraction from multiple formats

**Checks:**
- API connectivity and health
- SQL extraction from response
- SQL similarity to expected (70%+ keyword overlap)
- Response timeout handling

**Usage:**
```bash
# Start Docker container first
docker-compose up -d

# Run test
python test/test_api_questions.py
```

**Output:**
- Console log with API responses and extracted SQL
- `test/logs/test_api_questions_YYYYMMDD_HHMMSS.log`
- `test/logs/test_api_questions_report.json`

**Documentation:**
- See `API_TESTING.md` for detailed information

## Log Files

All test logs are saved to `test/logs/` with timestamps:
- `validate_training_YYYYMMDD_HHMMSS.log`
- `test_all_questions_YYYYMMDD_HHMMSS.log`
- `run_all_tests_YYYYMMDD_HHMMSS.log`

JSON reports are also saved for structured data analysis:
- `validate_training_report.json`
- `test_all_questions_report.json`
- `run_all_tests_report.json`

## Test Results

### Current Status
- Training data validation: **PASSING** (4/5 checks)
  - ✅ schema.json: 35 tables
  - ✅ queries.json: 55 question-SQL pairs
  - ✅ documentation.json: 53 terms, 7 rules
  - ✅ samples.json: 16 sample tables
  - ⚠️ sql_patterns.json: 14 patterns (used for matching only)

- Knowledge base: **LOADED SUCCESSFULLY**
  - ✅ Azure OpenAI connection: OK
  - ✅ PostgreSQL database: OK
  - ✅ Training examples: 55 questions
  - ✅ Business terms: 53 defined

## Troubleshooting

### Tests fail to run
1. Verify Docker container is running: `docker-compose ps`
2. Check environment variables in `.env` file
3. Verify training data files exist: `ls training_data/`

### Knowledge base loading fails
1. Check Azure OpenAI connection
2. Check PostgreSQL connection strings
3. Review training data file formats

### SQL generation produces different results
This is expected behavior - the system can generate semantically equivalent SQL that differs syntactically from training examples. To verify correctness:
1. Review the generated SQL in the log files
2. Execute the SQL against the database manually
3. Compare results with expected output

## Adding New Tests

To add a new test:
1. Create a new script in `test/` folder (e.g., `test_my_feature.py`)
2. Import utilities from `conftest.py`:
   ```python
   from conftest import setup_logger, save_json_report
   ```
3. Set up logging:
   ```python
   logger, log_path = setup_logger("my_test", "my_test.log")
   ```
4. Log your test steps and results
5. Save JSON report at the end
6. Add the test to `run_all_tests.py` `TESTS` list

## Integration with CI/CD

To run tests in CI/CD pipeline:
```bash
cd /path/to/vanna2_eldad
python test/run_all_tests.py
```

The script returns:
- Exit code 0: All tests passed
- Exit code 1: One or more tests failed

## Notes

- All tests are designed to be independent and can run in any order
- Test execution is sequential to avoid resource conflicts
- Logs include timestamps, severity levels, and detailed error messages
- JSON reports can be parsed for automated result processing
