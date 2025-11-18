import calendar
from datetime import datetime, timedelta
import os
import shutil
import logging
import time
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = r"W:\db.sqlite3"
BACKUP_PATH = r"W:\backup"

def get_month_folder_name(month_number):
    """Get formatted month folder name with number prefix (e.g., '1 January')."""
    month_name = calendar.month_name[month_number]
    return f"{month_number} {month_name}"

def pregenerate_folders():
    """Pregenerate year and month folders for current year and next year."""
    current_date = datetime.now()
    current_year = current_date.year
    next_year = current_year + 1
    
    for year in [current_year, next_year]:
        year_folder = os.path.join(BACKUP_PATH, str(year))
        os.makedirs(year_folder, exist_ok=True)
        logging.info(f"Ensured year folder exists: {year_folder}")
        
        for month in range(1, 13):
            month_folder_name = get_month_folder_name(month)
            month_folder = os.path.join(year_folder, month_folder_name)
            os.makedirs(month_folder, exist_ok=True)
            logging.debug(f"Ensured month folder exists: {month_folder}")

def get_backup_files_sorted():
    """Get all backup files sorted by date (oldest first)."""
    backup_files = []
    for root, dirs, files in os.walk(BACKUP_PATH):
        for file in files:
            if file.endswith(".sqlite3") and "db_backup_" in file:
                file_path = os.path.join(root, file)
                try:
                    # Extract timestamp from filename: db_backup_YYYY-MM-DD_HH-MM-SS.sqlite3
                    timestamp_str = file.replace("db_backup_", "").replace(".sqlite3", "")
                    file_date = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                    backup_files.append((file_date, file_path))
                except ValueError:
                    # If parsing fails, use file modification time as fallback
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append((file_date, file_path))
    
    # Sort by date (oldest first)
    backup_files.sort(key=lambda x: x[0])
    return backup_files

def ensure_sufficient_space(required_bytes, buffer_percent=10):
    """Ensure sufficient space is available, deleting oldest backups if necessary."""
    # Calculate required space with buffer
    required_space = required_bytes * (1 + buffer_percent / 100)
    
    # Get disk usage for the backup drive
    backup_drive = os.path.splitdrive(BACKUP_PATH)[0] + "\\"
    total, used, free = shutil.disk_usage(backup_drive)
    
    logging.info(f"Disk space check - Free: {free / (1024**3):.2f} GB, Required: {required_space / (1024**3):.2f} GB")
    
    if free >= required_space:
        logging.info("Sufficient space available")
        return True
    
    logging.warning(f"Insufficient space. Need to free {(required_space - free) / (1024**3):.2f} GB")
    
    # Get sorted backup files (oldest first)
    backup_files = get_backup_files_sorted()
    
    if not backup_files:
        logging.error("No backup files found to delete")
        return False
    
    # Delete oldest backups until we have enough space
    deleted_count = 0
    freed_space = 0
    
    for file_date, file_path in backup_files:
        if free + freed_space >= required_space:
            break
        
        try:
            file_size = os.path.getsize(file_path)
            os.remove(file_path)
            freed_space += file_size
            deleted_count += 1
            logging.info(f"Deleted oldest backup: {file_path} ({file_size / (1024**2):.2f} MB)")
            
            # Check if the month folder is now empty and can be deleted
            month_folder = os.path.dirname(file_path)
            if os.path.exists(month_folder):
                remaining_files = [f for f in os.listdir(month_folder) if f.endswith(".sqlite3")]
                if not remaining_files:
                    os.rmdir(month_folder)
                    logging.info(f"Removed empty month folder: {month_folder}")
            
            # Check if the year folder is now empty and can be deleted
            year_folder = os.path.dirname(month_folder)
            if os.path.exists(year_folder):
                remaining_dirs = [d for d in os.listdir(year_folder) if os.path.isdir(os.path.join(year_folder, d))]
                if not remaining_dirs:
                    os.rmdir(year_folder)
                    logging.info(f"Removed empty year folder: {year_folder}")
                    
        except Exception as e:
            logging.error(f"Error deleting backup file {file_path}: {e}")
    
    # Recheck disk space
    total, used, free = shutil.disk_usage(backup_drive)
    
    if free >= required_space:
        logging.info(f"Freed {freed_space / (1024**3):.2f} GB by deleting {deleted_count} backup(s)")
        return True
    else:
        logging.error(f"Still insufficient space after deleting {deleted_count} backup(s)")
        return False

def create_backup():
    """Create a backup of the database."""
    # Pregenerate folders for current and next year
    pregenerate_folders()
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        logging.error(f"Database file not found: {DB_PATH}")
        return False
    
    # Get database file size
    db_size = os.path.getsize(DB_PATH)
    logging.info(f"Database size: {db_size / (1024**2):.2f} MB")
    
    # Ensure sufficient space before backup
    if not ensure_sufficient_space(db_size):
        logging.error("Cannot create backup: insufficient space even after cleanup")
        return False
    
    current_date = datetime.now()
    
    # Create a folder for the year
    year_folder = os.path.join(BACKUP_PATH, str(current_date.year))
    os.makedirs(year_folder, exist_ok=True)
    logging.info(f"Created year folder: {year_folder}")
    
    # Create a folder for the month with numbered prefix
    month_folder_name = get_month_folder_name(current_date.month)
    month_folder = os.path.join(year_folder, month_folder_name)
    os.makedirs(month_folder, exist_ok=True)
    logging.info(f"Created month folder: {month_folder}")
    
    # Copy the file to the folder
    backup_file = os.path.join(month_folder, f"db_backup_{current_date.strftime('%Y-%m-%d_%H-%M-%S')}.sqlite3")
    shutil.copy(DB_PATH, backup_file)
    logging.info(f"Copied database to: {backup_file}")

    logging.info(f"Backup file created at: {backup_file}")
    return True

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
