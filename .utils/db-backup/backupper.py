import calendar
from datetime import datetime, timedelta
import os
import shutil
import logging
import time
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = r"Y:\micro\micro\db.sqlite3"
BACKUP_PATH = r"W:\backup"

def create_backup():
    """Create a backup of the database."""
    current_date = datetime.now()
    
    # Create a folder for the year
    year_folder = os.path.join(BACKUP_PATH, str(current_date.year))
    os.makedirs(year_folder, exist_ok=True)
    logging.info(f"Created year folder: {year_folder}")
    
    # Create a folder for the month
    month_name = current_date.strftime("%B")  # e.g., 'May'
    month_folder = os.path.join(year_folder, month_name)
    os.makedirs(month_folder, exist_ok=True)
    logging.info(f"Created month folder: {month_folder}")
    
    # Copy the file to the folder
    backup_file = os.path.join(month_folder, f"db_backup_{current_date.strftime('%Y-%m-%d_%H-%M-%S')}.sqlite3")
    shutil.copy(DB_PATH, backup_file)
    logging.info(f"Copied database to: {backup_file}")

    logging.info(f"Backup file created at: {backup_file}")

def schedule_backups(interval_hours=24):
    """Schedule backups at a specified interval (default is every 24 hours)."""
    while True:
        create_backup()
        logging.info(f"Next backup scheduled in {interval_hours} hours.")
        time.sleep(interval_hours * 3600)  # Convert hours to seconds

def reveal_backups():
    """Reveal the backup files."""
    for root, dirs, files in os.walk(BACKUP_PATH):
        for file in files:
            if file.endswith(".sqlite3"):
                logging.info(f"Backup found: {os.path.join(root, file)}")

def main():
    parser = argparse.ArgumentParser(description="Database Backup Utility")
    parser.add_argument('-b', '--backup', action='store_true', help='Perform a single backup')
    parser.add_argument('-r', '--reveal', action='store_true', help='Reveal backup files')
    parser.add_argument('-c', '--cron', type=int, help='Schedule backups every n hours')

    args = parser.parse_args()

    if args.backup:
        create_backup()
    elif args.reveal:
        reveal_backups()
    elif args.cron is not None:
        schedule_backups(args.cron)
    else:
        parser.print_help()
        exit(1)  # Exit with a non-zero status to indicate no arguments were provided

if __name__ == "__main__":
    main()
