"""
Master test runner - Executes all tests with unified logging and reporting
Logs results to: test/logs/run_all_tests_YYYYMMDD_HHMMSS.log

Available tests:
  - validate_training.py: Validates training data files and knowledge base
  - test_all_questions.py: Tests all 55 training questions
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import setup_logger

# Setup logger
logger, log_path = setup_logger("run_all_tests", "run_all_tests.log")

TEST_DIR = Path(__file__).parent
TESTS = [
    ("validate_training.py", "Validate Training Data"),
    ("test_all_questions.py", "Test All Questions"),
    ("test_api_questions.py", "Test Questions via API"),
]


def run_test(test_file, test_name):
    """Run a single test and return results"""
    logger.info(f"\n{'='*70}")
    logger.info(f"Running: {test_name}")
    logger.info(f"Script: {test_file}")
    logger.info(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(TEST_DIR / test_file)],
            cwd=str(TEST_DIR.parent),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Log output
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        
        success = result.returncode == 0
        logger.info(f"\n✅ PASSED" if success else f"\n❌ FAILED (exit code: {result.returncode})")
        
        return {
            "name": test_name,
            "script": test_file,
            "success": success,
            "exit_code": result.returncode,
            "stdout_lines": len(result.stdout.split('\n')) if result.stdout else 0,
            "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0
        }
    
    except subprocess.TimeoutExpired:
        logger.error(f"❌ TIMEOUT - Test exceeded 300 seconds")
        return {
            "name": test_name,
            "script": test_file,
            "success": False,
            "exit_code": None,
            "error": "Timeout"
        }
    
    except Exception as e:
        logger.error(f"❌ ERROR - {e}")
        return {
            "name": test_name,
            "script": test_file,
            "success": False,
            "exit_code": None,
            "error": str(e)
        }


def main():
    """Run all tests"""
    logger.info("\n" + "="*70)
    logger.info("TEST SUITE RUNNER".center(70))
    logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(70))
    logger.info("="*70 + "\n")
    
    # Run all tests
    results = []
    passed = 0
    failed = 0
    
    for test_file, test_name in TESTS:
        result = run_test(test_file, test_name)
        results.append(result)
        
        if result['success']:
            passed += 1
        else:
            failed += 1
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📋 TEST SUITE SUMMARY")
    logger.info("="*70)
    logger.info(f"  Total Tests: {len(TESTS)}")
    logger.info(f"  ✅ Passed: {passed}")
    logger.info(f"  ❌ Failed: {failed}\n")
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        logger.info(f"  {status} - {result['name']}")
    
    logger.info(f"\n  Pass Rate: {100 * passed / len(TESTS):.1f}%")
    
    if failed == 0:
        logger.info("\n  🎉 ALL TESTS PASSED!")
    else:
        logger.info(f"\n  ⚠️  {failed} test suite(s) failed")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(TESTS),
            "passed": passed,
            "failed": failed,
            "pass_rate": 100 * passed / len(TESTS) if TESTS else 0
        },
        "tests": results
    }
    
    report_path = TEST_DIR / "logs" / "run_all_tests_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\n📄 Report saved to: {report_path}")
    logger.info(f"📄 Log file: {log_path}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
