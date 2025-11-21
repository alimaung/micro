#!/usr/bin/env python3
"""
Script to vacuum (compact) the SQLite database to reclaim space after dropping tables.
"""

import sqlite3
import os
from pathlib import Path


def vacuum_database(db_path):
    """Vacuum the database to reclaim space."""
    if not os.path.exists(db_path):
        print(f"Error: Database file not found: {db_path}")
        return
    
    # Get initial size
    initial_size = os.path.getsize(db_path)
    initial_size_mb = initial_size / (1024 * 1024)
    
    print(f"Database: {db_path}")
    print(f"Initial size: {initial_size_mb:.2f} MB ({initial_size:,} bytes)")
    print("-" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        
        print("Running VACUUM...")
        conn.execute("VACUUM")
        conn.close()
        
        # Get final size
        final_size = os.path.getsize(db_path)
        final_size_mb = final_size / (1024 * 1024)
        space_reclaimed = initial_size - final_size
        space_reclaimed_mb = space_reclaimed / (1024 * 1024)
        
        print("-" * 60)
        print(f"Final size: {final_size_mb:.2f} MB ({final_size:,} bytes)")
        print(f"Space reclaimed: {space_reclaimed_mb:.2f} MB ({space_reclaimed:,} bytes)")
        print(f"Reduction: {(space_reclaimed / initial_size * 100):.2f}%")
        
    except Exception as e:
        print(f"Error vacuuming database: {e}")


if __name__ == "__main__":
    # Get the database path (same directory as script)
    script_dir = Path(__file__).parent
    db_path = script_dir / "db.sqlite3"
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        print("Please ensure db.sqlite3 exists in the same directory as this script.")
    else:
        vacuum_database(str(db_path))


