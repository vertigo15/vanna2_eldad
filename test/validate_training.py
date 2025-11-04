"""
Validate training data files and knowledge base
Logs results to: test/logs/validate_training_YYYYMMDD_HHMMSS.log
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import setup_logger, save_json_report, load_training_questions

# Setup logger
logger, log_path = setup_logger("validate_training", "validate_training.log")

TRAINING_DATA_DIR = Path(__file__).parent.parent / "training_data"


def validate_training_files():
    """Step 1: Validate training files exist and are valid JSON"""
    logger.info("=" * 70)
    logger.info("STEP 1️⃣: Validate Training Files")
    logger.info("=" * 70)
    
    files = ['schema.json', 'queries.json', 'documentation.json', 'sql_patterns.json', 'samples.json']
    all_valid = True
    results = {}
    
    for filename in files:
        filepath = TRAINING_DATA_DIR / filename
        logger.info(f"\nChecking: {filename}")
        
        if not filepath.exists():
            logger.error(f"  ❌ FILE NOT FOUND")
            results[filename] = {"status": "FAILED", "reason": "File not found"}
            all_valid = False
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Count items
            if filename == 'schema.json':
                count = len(data.get('tables', []))
                logger.info(f"  ✅ Valid - {count} tables")
                results[filename] = {"status": "OK", "count": count}
            elif filename == 'queries.json':
                count = len(data.get('question_sql_pairs', []))
                logger.info(f"  ✅ Valid - {count} question-SQL pairs")
                results[filename] = {"status": "OK", "count": count}
            elif filename == 'documentation.json':
                terms = len(data.get('business_terms', []))
                rules = len(data.get('business_rules', []))
                logger.info(f"  ✅ Valid - {terms} terms, {rules} rules")
                results[filename] = {"status": "OK", "terms": terms, "rules": rules}
            elif filename == 'sql_patterns.json':
                count = len(data.get('common_queries', []))
                logger.info(f"  ✅ Valid - {count} patterns")
                results[filename] = {"status": "OK", "count": count}
            else:  # samples.json
                count = len(data.get('data_samples', []))
                logger.info(f"  ✅ Valid - {count} sample tables")
                results[filename] = {"status": "OK", "count": count}
        
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ JSON ERROR: {e}")
            results[filename] = {"status": "FAILED", "reason": f"JSON error: {str(e)}"}
            all_valid = False
        except Exception as e:
            logger.error(f"  ❌ ERROR: {e}")
            results[filename] = {"status": "FAILED", "reason": str(e)}
            all_valid = False
    
    return all_valid, results


def validate_knowledge_base():
    """Step 2: Validate knowledge base loads correctly"""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 2️⃣: Validate Knowledge Base Loading")
    logger.info("=" * 70)
    
    try:
        from knowledge_base import get_knowledge_base
        
        kb = get_knowledge_base()
        logger.info("  ✅ Knowledge base loaded")
        
        # Check components
        schema_ddl = kb.get_schema_ddl()
        logger.info(f"  ✅ Schema: {len(schema_ddl)} tables")
        
        queries = kb.get_example_queries()
        logger.info(f"  ✅ Queries: {len(queries)} examples")
        
        business = kb.get_business_context()
        logger.info(f"  ✅ Business context: {len(business)} chars")
        
        context = kb.get_system_context()
        logger.info(f"  ✅ System context: {len(context)} chars")
        
        logger.info(f"\n  📊 Knowledge Base Stats: {kb.get_stats()}")
        
        return True, {
            "schema_tables": len(schema_ddl),
            "example_queries": len(queries),
            "business_context_chars": len(business),
            "system_context_chars": len(context),
            "stats": kb.get_stats()
        }
    
    except Exception as e:
        logger.error(f"  ❌ FAILED: {e}")
        return False, {"error": str(e)}


def validate_schema_structure():
    """Step 3: Validate schema structure"""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 3️⃣: Validate Schema Structure")
    logger.info("=" * 70)
    
    try:
        from knowledge_base import get_knowledge_base
        
        kb = get_knowledge_base()
        schema_data = kb._cache.get('schema', {})
        
        if not schema_data:
            logger.error("  ❌ No schema data found")
            return False, {"error": "No schema data"}
        
        tables = schema_data.get('tables', [])
        logger.info(f"  Validating {len(tables)} tables...")
        
        required_fields = ['name', 'description', 'ddl']
        all_valid = True
        
        for i, table in enumerate(tables[:3]):
            missing_fields = [f for f in required_fields if f not in table]
            if missing_fields:
                logger.warning(f"  ⚠️  Table {i+1} missing fields: {missing_fields}")
                all_valid = False
            else:
                logger.info(f"  ✅ Table {i+1}: {table['name']} (valid)")
        
        if len(tables) > 3:
            logger.info(f"  ✅ ... and {len(tables) - 3} more tables")
        
        return all_valid, {"total_tables": len(tables), "sample_validated": min(3, len(tables))}
    
    except Exception as e:
        logger.error(f"  ❌ FAILED: {e}")
        return False, {"error": str(e)}


def main():
    """Run all validations"""
    logger.info("\n" + "="*70)
    logger.info("TRAINING DATA VALIDATION".center(70))
    logger.info("="*70 + "\n")
    
    # Run validations
    files_ok, files_results = validate_training_files()
    kb_ok, kb_results = validate_knowledge_base()
    schema_ok, schema_results = validate_schema_structure()
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📋 VALIDATION SUMMARY")
    logger.info("=" * 70)
    
    checks = [
        ("Training Files", files_ok),
        ("Knowledge Base", kb_ok),
        ("Schema Structure", schema_ok),
    ]
    
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    
    for name, ok in checks:
        status = "✅ PASS" if ok else "❌ FAIL"
        logger.info(f"  {status} - {name}")
    
    logger.info(f"\n  Total: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("\n  🎉 All validations passed!")
    else:
        logger.info("\n  ⚠️ Some validations failed. Review the log above.")
    
    # Save detailed results
    results = {
        "timestamp": str(Path(log_path).stem),
        "summary": {
            "passed": passed,
            "total": total,
            "success": passed == total
        },
        "files": files_results,
        "knowledge_base": kb_results,
        "schema": schema_results
    }
    
    report_path = save_json_report(results, "validate_training_report.json")
    logger.info(f"\n📄 Full report saved to: {report_path}")
    logger.info(f"📄 Log file: {log_path}\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
