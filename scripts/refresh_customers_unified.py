"""
Refresh Customers Unified Table

Lightweight script to refresh the customers_unified table.
Can be scheduled to run daily/hourly via cron or cloud scheduler.

Usage:
    python scripts/refresh_customers_unified.py
    python scripts/refresh_customers_unified.py --incremental  # Future: incremental updates
"""
import sys
import os
from pathlib import Path
import argparse
import logging
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for refresh script"""
    parser = argparse.ArgumentParser(description='Refresh the customers_unified table')
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Use incremental refresh (future optimization, not yet implemented)'
    )
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("  Customers Unified Table - Refresh")
    logger.info("="*70)
    logger.info(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.incremental:
        logger.warning("  --incremental flag detected but not yet implemented")
        logger.warning("  Falling back to full refresh")
    
    logger.info("")
    
    try:
        # Import and run the build function
        from build_customers_unified_table import build_customers_unified_table
        
        build_customers_unified_table()
        
        logger.info("="*70)
        logger.info("  ✓ Refresh Complete!")
        logger.info(f"  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error("="*70)
        logger.error("  ❌ Refresh Failed!")
        logger.error(f"  Error: {str(e)}")
        logger.error("="*70)
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()

