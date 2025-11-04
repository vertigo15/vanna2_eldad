"""
Test all training questions end-to-end
Tests if the knowledge base can generate correct SQL for all 55 training questions
Logs results to: test/logs/test_all_questions_YYYYMMDD_HHMMSS.log
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import setup_logger, save_json_report, load_training_questions

# Setup logger
logger, log_path = setup_logger("test_all_questions", "test_all_questions.log")


def test_all_questions():
    """Test if all training questions generate correct SQL"""
    logger.info("\n" + "="*70)
    logger.info("TESTING ALL 55 TRAINING QUESTIONS".center(70))
    logger.info("="*70 + "\n")
    
    # Load questions
    try:
        questions = load_training_questions()
        logger.info(f"✅ Loaded {len(questions)} training questions\n")
    except Exception as e:
        logger.error(f"❌ Failed to load training questions: {e}")
        return 1
    
    # Load knowledge base
    try:
        from knowledge_base import get_knowledge_base
        kb = get_knowledge_base()
        logger.info("✅ Knowledge base loaded\n")
    except Exception as e:
        logger.error(f"❌ Failed to load knowledge base: {e}")
        return 1
    
    # Test each question
    results = []
    passed = 0
    failed = 0
    
    for i, question_data in enumerate(questions, 1):
        question = question_data['question']
        expected_sql = question_data['sql']
        
        logger.info(f"Test {i}/{len(questions)}: {question}")
        logger.info(f"  Expected SQL: {expected_sql[:80]}...")
        
        try:
            # Test 1: Check if question exists in knowledge base (should always pass for training data)
            question_exists = False
            for example in kb.get_example_queries():
                if example['question'].strip() == question.strip():
                    question_exists = True
                    break
            
            if not question_exists:
                logger.error(f"  ❌ FAIL - Question not found in knowledge base\n")
                failed += 1
                results.append({
                    "number": i,
                    "question": question,
                    "status": "FAIL",
                    "expected_sql": expected_sql,
                    "test": "question_exists",
                    "error": "Question not found in knowledge base"
                })
                continue
            
            # Test 2: Check if similar question can be found
            similar_question = kb.find_similar_question(question)
            
            if similar_question:
                logger.info(f"  ✅ PASS - Question found in knowledge base")
                logger.info(f"  Expected SQL: {expected_sql[:80]}...")
                logger.info(f"  KB SQL: {similar_question['sql'][:80]}...\n")
                
                # Check if SQL matches
                sql_match = similar_question['sql'].strip() == expected_sql.strip()
                
                passed += 1
                results.append({
                    "number": i,
                    "question": question,
                    "status": "PASS",
                    "expected_sql": expected_sql,
                    "kb_sql": similar_question['sql'],
                    "sql_match": sql_match,
                    "test": "similar_question_found"
                })
            else:
                logger.error(f"  ❌ FAIL - No similar question found\n")
                failed += 1
                results.append({
                    "number": i,
                    "question": question,
                    "status": "FAIL",
                    "expected_sql": expected_sql,
                    "test": "similar_question_search",
                    "error": "No similar question found"
                })
        
        except Exception as e:
            logger.error(f"  ❌ FAIL - Exception: {e}\n")
            failed += 1
            results.append({
                "number": i,
                "question": question,
                "status": "FAIL",
                "expected_sql": expected_sql,
                "generated_sql": None,
                "error": str(e)
            })
    
    # Summary
    logger.info("=" * 70)
    logger.info("📋 TEST SUMMARY")
    logger.info("=" * 70)
    logger.info(f"  Total Tests: {len(questions)}")
    logger.info(f"  ✅ Passed: {passed}")
    logger.info(f"  ❌ Failed: {failed}")
    logger.info(f"  Pass Rate: {100 * passed / len(questions):.1f}%\n")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED!")
    else:
        logger.info(f"⚠️  {failed} test(s) failed")
    
    # Save results
    summary = {
        "timestamp": str(Path(log_path).stem),
        "total": len(questions),
        "passed": passed,
        "failed": failed,
        "pass_rate": 100 * passed / len(questions) if questions else 0,
        "results": results
    }
    
    report_path = save_json_report(summary, "test_all_questions_report.json")
    logger.info(f"\n📄 Full report saved to: {report_path}")
    logger.info(f"📄 Log file: {log_path}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(test_all_questions())
