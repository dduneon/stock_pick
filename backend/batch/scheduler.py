"""
KOSPI Stock Data Collection Scheduler

This module provides daily scheduled execution of stock data collection
at Korean market close time (15:30 KST).

Usage:
    python -m backend.batch.scheduler
"""

import time
import os
import sys
from datetime import datetime
from typing import Optional

import schedule

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.batch.run_batch import run_batch_job, setup_logging


# Market close time in KST (24-hour format)
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30


def is_weekday() -> bool:
    """Check if today is a weekday (Mon-Fri)."""
    today = datetime.now()
    return today.weekday() < 5  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday


def scheduled_job():
    """Job to be run at scheduled time."""
    logger = setup_logging()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Scheduled job triggered at {current_time}")
    
    # Skip weekends - Korean stock market is closed
    if not is_weekday():
        logger.info("Today is a weekend. Skipping data collection (market closed).")
        return
    
    # Run the batch job
    run_batch_job()


def run_scheduler(once: bool = False, test_time: Optional[str] = None):
    """
    Run the scheduler.
    
    Args:
        once: If True, run once immediately and exit (for testing)
        test_time: If provided, schedule at this time instead (HH:MM format)
    """
    logger = setup_logging()
    
    if once:
        logger.info("Running in single-execution mode")
        run_batch_job()
        return
    
    # Schedule the job
    if test_time:
        schedule.every().day.at(test_time).do(scheduled_job)
        logger.info(f"Scheduled job set to run daily at {test_time}")
    else:
        schedule_time = f"{MARKET_CLOSE_HOUR:02d}:{MARKET_CLOSE_MINUTE:02d}"
        schedule.every().day.at(schedule_time).do(scheduled_job)
        logger.info(f"Scheduled job set to run daily at {schedule_time} KST (market close)")
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    logger.info("Waiting for scheduled time...")
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        raise


def main():
    """Main entry point for the scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="KOSPI Stock Data Collection Scheduler"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once immediately and exit (for testing)"
    )
    parser.add_argument(
        "--test-time",
        type=str,
        help="Schedule at specific time for testing (HH:MM format, e.g., '09:00')"
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run the batch job immediately (alias for --once)"
    )
    
    args = parser.parse_args()
    
    # Handle --run-now as alias for --once
    run_once = args.once or args.run_now
    
    run_scheduler(once=run_once, test_time=args.test_time)


if __name__ == "__main__":
    main()
