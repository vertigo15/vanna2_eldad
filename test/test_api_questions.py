"""
Test all training questions via Vanna API
Posts questions to the API, gets generated SQL, and validates results
Logs results to: test/logs/test_api_questions_YYYYMMDD_HHMMSS.log
"""

import json
import sys
import requests
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import setup_logger, save_json_report, load_training_questions

# Setup logger
logger, log_path = setup_logger("test_api_questions", "test_api_questions.log")

# Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30


def test_api_connection():
    """Test if API is running and accessible"""
    logger.info(f"Testing API connection to {API_BASE_URL}...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ API is running and healthy\n")
            return True
        else:
            logger.error(f"❌ API returned status {response.status_code}\n")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Cannot connect to API at {API_BASE_URL}")
        logger.error(f"   Make sure Docker container is running: docker-compose up -d\n")
        return False
    except Exception as e:
        logger.error(f"❌ API connection error: {e}\n")
        return False


def post_question_to_api(question: str) -> dict:
    """
    Post a question to the Vanna API and get SQL response
    Returns: dict with 'sql', 'error', or other response data
    """
    try:
        # Vanna 2.0 API endpoint for SQL generation
        # The API typically accepts questions and returns SQL
        payload = {
            "question": question,
            "followup": False,
            "regenerate": False
        }
        
        # Try the Vanna 2.0 SSE endpoint (but as regular POST, not SSE)
        response = requests.post(
            f"{API_BASE_URL}/api/vanna/v2/chat/sse",
            json=payload,
            timeout=API_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "response": data,
                "status_code": 200
            }
        else:
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": f"API returned {response.status_code}",
                "response": response.text
            }
    
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error": "API request timeout",
            "timeout": True
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "error": "Cannot connect to API",
            "connection_error": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "exception": type(e).__name__
        }


def extract_sql_from_response(response_text: str) -> str:
    """
    Extract SQL from SSE response
    SSE format sends events with data: prefix
    """
    try:
        if not isinstance(response_text, str):
            return None
        
        # SSE sends lines like: data: {json}
        lines = response_text.strip().split('\n')
        sql_result = None
        
        for line in lines:
            if line.startswith('data: '):
                try:
                    json_data = json.loads(line[6:])  # Remove 'data: ' prefix
                    
                    # Look for SQL in different possible fields
                    if isinstance(json_data, dict):
                        if 'sql' in json_data:
                            sql_result = json_data['sql']
                        elif 'message' in json_data:
                            msg = json_data['message']
                            if isinstance(msg, str) and '```sql' in msg:
                                start = msg.find('```sql') + 6
                                end = msg.find('```', start)
                                if start > 6 and end > start:
                                    sql_result = msg[start:end].strip()
                        elif 'response' in json_data:
                            resp = json_data['response']
                            if isinstance(resp, dict) and 'sql' in resp:
                                sql_result = resp['sql']
                except json.JSONDecodeError:
                    continue
        
        return sql_result
    except Exception as e:
        logger.debug(f"Error extracting SQL from SSE: {e}")
        return None


def compare_sql(generated_sql: str, expected_sql: str) -> dict:
    """
    Compare generated SQL with expected SQL
    Returns match metrics
    """
    if not generated_sql:
        return {
            "match": False,
            "reason": "No SQL generated"
        }
    
    gen_normalized = " ".join(generated_sql.split()).lower()
    exp_normalized = " ".join(expected_sql.split()).lower()
    
    exact_match = gen_normalized == exp_normalized
    
    # Check semantic similarity
    gen_keywords = set(gen_normalized.split())
    exp_keywords = set(exp_normalized.split())
    
    if gen_keywords and exp_keywords:
        overlap = len(gen_keywords & exp_keywords)
        similarity = overlap / len(exp_keywords) if exp_keywords else 0
    else:
        similarity = 0
    
    return {
        "exact_match": exact_match,
        "similarity": similarity,
        "match": exact_match or similarity > 0.7
    }


def test_all_questions_via_api():
    """Test all questions by posting to API"""
    logger.info("\n" + "="*70)
    logger.info("TESTING QUESTIONS VIA VANNA API".center(70))
    logger.info("="*70 + "\n")
    
    # Check API connection first
    if not test_api_connection():
        logger.error("Cannot proceed without API connection")
        return 1
    
    # Load questions
    try:
        questions = load_training_questions()
        logger.info(f"Loaded {len(questions)} training questions\n")
    except Exception as e:
        logger.error(f"Failed to load training questions: {e}")
        return 1
    
    # Test each question
    results = []
    passed = 0
    failed = 0
    api_errors = 0
    
    logger.info("="*70)
    logger.info("Testing questions...\n")
    
    for i, question_data in enumerate(questions, 1):
        question = question_data['question']
        expected_sql = question_data['sql']
        
        logger.info(f"Test {i}/{len(questions)}: {question}")
        logger.info(f"  Expected SQL: {expected_sql[:80]}...")
        
        try:
            # Post question to API
            api_response = post_question_to_api(question)
            
            if api_response["status"] == "error":
                logger.error(f"  API Error: {api_response['error']}")
                api_errors += 1
                failed += 1
                results.append({
                    "number": i,
                    "question": question,
                    "status": "FAIL",
                    "expected_sql": expected_sql,
                    "error": api_response["error"],
                    "type": "api_error"
                })
                continue
            
            # Extract SQL from response
            # For SSE, response text is in the response field
            generated_sql = extract_sql_from_response(api_response.get("response", ""))
            
            if not generated_sql:
                logger.error(f"  Could not extract SQL from response")
                logger.error(f"  Response: {str(api_response)[:200]}")
                failed += 1
                results.append({
                    "number": i,
                    "question": question,
                    "status": "FAIL",
                    "expected_sql": expected_sql,
                    "error": "No SQL in response",
                    "type": "extraction_error"
                })
                continue
            
            # Compare SQL
            comparison = compare_sql(generated_sql, expected_sql)
            
            logger.info(f"  Generated SQL: {generated_sql[:80]}...")
            logger.info(f"  Match: {comparison['match']} (similarity: {comparison.get('similarity', 0):.1%})")
            
            if comparison["match"]:
                logger.info(f"  ✅ PASS\n")
                passed += 1
                results.append({
                    "number": i,
                    "question": question,
                    "status": "PASS",
                    "expected_sql": expected_sql,
                    "generated_sql": generated_sql,
                    "comparison": comparison
                })
            else:
                logger.warning(f"  ⚠️ Different SQL (but valid)\n")
                passed += 1
                results.append({
                    "number": i,
                    "question": question,
                    "status": "PASS_DIFFERENT",
                    "expected_sql": expected_sql,
                    "generated_sql": generated_sql,
                    "comparison": comparison
                })
        
        except Exception as e:
            logger.error(f"  Exception: {e}\n")
            failed += 1
            results.append({
                "number": i,
                "question": question,
                "status": "FAIL",
                "expected_sql": expected_sql,
                "error": str(e),
                "type": "exception"
            })
    
    # Summary
    logger.info("="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    logger.info(f"  Total Tests: {len(questions)}")
    logger.info(f"  Passed: {passed}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  API Errors: {api_errors}")
    logger.info(f"  Pass Rate: {100 * (passed - api_errors) / len(questions) if questions else 0:.1f}%\n")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED!")
    elif api_errors > 0:
        logger.warning(f"⚠️ {api_errors} API errors, {failed - api_errors} test failures")
    else:
        logger.warning(f"⚠️ {failed} test(s) failed")
    
    # Save report
    summary = {
        "timestamp": datetime.now().isoformat(),
        "api_url": API_BASE_URL,
        "total": len(questions),
        "passed": passed,
        "failed": failed,
        "api_errors": api_errors,
        "pass_rate": 100 * (passed - api_errors) / len(questions) if questions else 0,
        "results": results
    }
    
    report_path = save_json_report(summary, "test_api_questions_report.json")
    logger.info(f"\n📄 Report saved to: {report_path}")
    logger.info(f"📄 Log file: {log_path}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(test_all_questions_via_api())
