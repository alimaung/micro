#!/usr/bin/env python3
"""
Script to analyze SQLite database and find which tables take the most space.
"""

import sqlite3
import os
from pathlib import Path


def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def calculate_table_size(conn, table_name):
    """
    Calculate the actual size of a table by sampling rows and estimating.
    Returns size in bytes.
    """
    cursor = conn.cursor()
    
    try:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        if row_count == 0:
            return {'row_count': 0, 'estimated_size': 0, 'avg_row_size': 0}
        
        # Sample up to 1000 rows to calculate average row size
        sample_size = min(1000, row_count)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {sample_size}")
        sample_rows = cursor.fetchall()
        
        # Calculate average row size
        total_sample_size = 0
        for row in sample_rows:
            row_size = 0
            for value in row:
                if value is None:
                    row_size += 1  # NULL takes 1 byte
                elif isinstance(value, (int, float)):
                    row_size += 8  # Numbers are typically 8 bytes
                elif isinstance(value, bytes):
                    row_size += len(value)
                else:
                    row_size += len(str(value).encode('utf-8'))
            total_sample_size += row_size
        
        avg_row_size = total_sample_size / len(sample_rows) if sample_rows else 0
        estimated_size = row_count * avg_row_size
        
        return {
            'row_count': row_count,
            'estimated_size': estimated_size,
            'avg_row_size': avg_row_size
        }
        
    except sqlite3.Error as e:
        print(f"  Warning: Could not analyze {table_name}: {e}")
        return {'row_count': 0, 'estimated_size': 0, 'avg_row_size': 0}


def analyze_database(db_path):
    """Analyze the database and return table size information."""
    if not os.path.exists(db_path):
        print(f"Error: Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get database page size
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    
    # Get total page count
    cursor.execute("PRAGMA page_count")
    total_pages = cursor.fetchone()[0]
    total_size = total_pages * page_size
    
    print(f"Database: {db_path}")
    print(f"Page size: {page_size} bytes")
    print(f"Total pages: {total_pages:,}")
    print(f"Total database size: {format_size(total_size)}")
    print("-" * 60)
    
    # Get all table names
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    if not tables:
        print("No user tables found in the database.")
        conn.close()
        return
    
    print(f"\nAnalyzing {len(tables)} table(s)...\n")
    
    # Analyze each table
    table_info = []
    
    for table_name in tables:
        print(f"Analyzing {table_name}...", end='\r')
        
        # Get table schema info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Calculate actual table size using row sampling
        size_info = calculate_table_size(conn, table_name)
        
        table_info.append({
            'name': table_name,
            'row_count': size_info['row_count'],
            'estimated_size': size_info['estimated_size'],
            'avg_row_size': size_info['avg_row_size'],
            'column_count': len(columns)
        })
    
    print(" " * 50)  # Clear the progress line
    
    # Sort by estimated size (descending)
    table_info.sort(key=lambda x: x['estimated_size'], reverse=True)
    
    # Display results
    print(f"\n{'Table Name':<35} {'Rows':>15} {'Est. Size':>18} {'Avg Row':>12} {'Columns':>8}")
    print("-" * 95)
    
    for info in table_info:
        size_str = format_size(info['estimated_size'])
        avg_row_str = format_size(info['avg_row_size']) if info['avg_row_size'] > 0 else "N/A"
        print(f"{info['name']:<35} {info['row_count']:>15,} {size_str:>18} {avg_row_str:>12} {info['column_count']:>8}")
    
    # Calculate percentages
    total_estimated = sum(t['estimated_size'] for t in table_info)
    if total_estimated > 0:
        print("\n" + "=" * 95)
        print(f"{'Table Name':<35} {'Percentage':>15} {'Size':>18} {'Rows':>15}")
        print("-" * 95)
        for info in table_info:
            percentage = (info['estimated_size'] / total_estimated) * 100
            size_str = format_size(info['estimated_size'])
            print(f"{info['name']:<35} {percentage:>14.2f}% {size_str:>18} {info['row_count']:>15,}")
    
    conn.close()


if __name__ == "__main__":
    # Get the database path (same directory as script)
    script_dir = Path(__file__).parent
    db_path = script_dir / "db.sqlite3"
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        print("Please ensure db.sqlite3 exists in the same directory as this script.")
    else:
        analyze_database(str(db_path))

