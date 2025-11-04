"""
Common configuration and utilities for all tests
"""

import logging
import json
from pathlib import Path
from datetime import datetime

# Setup paths
TEST_DIR = Path(__file__).parent
LOGS_DIR = TEST_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create logger
def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    if log_file is None:
        log_file = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    log_path = LOGS_DIR / log_file
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler with UTF-8 encoding
    import io
    import sys
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    # Force UTF-8 encoding for Windows console
    if hasattr(console_handler, 'stream'):
        if hasattr(console_handler.stream, 'reconfigure'):
            try:
                console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
            except:
                pass
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_path


def save_json_report(data: dict, filename: str):
    """Save test results as JSON report"""
    report_path = LOGS_DIR / filename
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return report_path


def load_training_questions():
    """Load questions from training data"""
    training_data = Path(__file__).parent.parent / "training_data" / "queries.json"
    with open(training_data, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('question_sql_pairs', [])


if __name__ == "__main__":
    logger, path = setup_logger("test_config")
    logger.info(f"Test directory: {TEST_DIR}")
    logger.info(f"Logs directory: {LOGS_DIR}")
    logger.info(f"Test log created at: {path}")
