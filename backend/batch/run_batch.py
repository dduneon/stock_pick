"""
KOSPI Stock Data Collection - Batch Job Wrapper

This module wraps the data collection process with proper logging,
error handling, and execution tracking.

Usage:
    python -m backend.batch.run_batch
    python backend/batch/run_batch.py
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.batch.collect_data import collect_kospi_data, save_to_csv, save_to_json


# Configuration
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
DATA_DIR = os.path.join(project_root, "data")
LOG_RETENTION_DAYS = 7


def setup_logging() -> logging.Logger:
    """
    Setup logging with file rotation and console output.
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if not exists
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("batch_job")
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    # Log format
    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler with rotation (keep last 7 days)
    log_file = os.path.join(LOG_DIR, "batch_job.log")
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=LOG_RETENTION_DAYS,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def run_batch_job(date: Optional[str] = None) -> dict:
    """
    Execute the batch job for stock data collection.
    
    Args:
        date: Date string in YYYYMMDD format. Defaults to today.
    
    Returns:
        Dictionary with execution results:
        {
            'success': bool,
            'date': str,
            'records_collected': int,
            'csv_path': Optional[str],
            'json_path': Optional[str],
            'error': Optional[str]
        }
    """
    logger = setup_logging()
    
    # Set default date
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    result = {
        'success': False,
        'date': date,
        'records_collected': 0,
        'csv_path': None,
        'json_path': None,
        'error': None
    }
    
    logger.info("=" * 60)
    logger.info("Starting daily batch job")
    logger.info(f"Target date: {date}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Collect data
        logger.info("Step 1/3: Collecting KOSPI stock data...")
        df = collect_kospi_data(date)
        
        if df.empty:
            logger.warning("No data collected. This may be a market holiday.")
            result['error'] = "No data collected"
            return result
        
        records_count = len(df)
        result['records_collected'] = records_count
        logger.info(f"Collected {records_count} stocks")
        
        # Step 2: Save to CSV
        logger.info("Step 2/3: Saving to CSV...")
        csv_path = save_to_csv(df, date, output_dir=DATA_DIR)
        result['csv_path'] = csv_path
        logger.info(f"Saved to {csv_path}")
        
        # Step 3: Save to JSON
        logger.info("Step 3/3: Saving to JSON...")
        json_path = save_to_json(df, date, output_dir=DATA_DIR)
        result['json_path'] = json_path
        logger.info(f"Saved to {json_path}")
        
        # Success
        result['success'] = True
        logger.info("=" * 60)
        logger.info("Batch job completed successfully")
        logger.info(f"Total records: {records_count}")
        logger.info(f"CSV: {csv_path}")
        logger.info(f"JSON: {json_path}")
        logger.info("=" * 60)
        
    except Exception as e:
        error_msg = str(e)
        result['error'] = error_msg
        logger.error(f"Batch job failed: {error_msg}")
        logger.exception("Full traceback:")
    
    return result


def main():
    """Main entry point for the batch job."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="KOSPI Stock Data Collection Batch Job"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Date to collect data for (YYYYMMDD format). Defaults to today."
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of stocks to collect (for testing)"
    )
    
    args = parser.parse_args()
    
    # Run the batch job
    result = run_batch_job(date=args.date)
    
    # Exit with appropriate code
    if result['success']:
        print(f"\n✓ Batch job completed: {result['records_collected']} records collected")
        sys.exit(0)
    else:
        print(f"\n✗ Batch job failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
