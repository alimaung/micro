"""
Excel Report Generator for Microfilm Analysis Database

This script reads data from the SQLite analysis database and generates
comprehensive Excel reports for easy viewing and analysis.
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

def connect_to_database(db_path):
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        print(f"✅ Connected to database: {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def generate_projects_report(conn, output_dir):
    """Generate projects overview report."""
    query = """
    SELECT 
        p.project_id,
        p.archive_id,
        p.location,
        p.doc_type,
        p.folderName as project_folder,
        p.oversized as has_oversized,
        p.total_pages,
        p.total_pages_with_refs,
        COUNT(DISTINCT r.roll_id) as total_rolls,
        COUNT(DISTINCT CASE WHEN r.film_type = '16mm' THEN r.roll_id END) as rolls_16mm,
        COUNT(DISTINCT CASE WHEN r.film_type = '35mm' THEN r.roll_id END) as rolls_35mm,
        SUM(CASE WHEN r.film_type = '16mm' THEN r.pages_used ELSE 0 END) as pages_16mm,
        SUM(CASE WHEN r.film_type = '35mm' THEN r.pages_used ELSE 0 END) as pages_35mm,
        COUNT(DISTINCT d.document_id) as total_documents,
        COUNT(DISTINCT CASE WHEN d.is_oversized = 1 THEN d.document_id END) as documents_with_oversized,
        p.date_created
    FROM Projects p
    LEFT JOIN Rolls r ON p.project_id = r.project_id
    LEFT JOIN Documents d ON r.roll_id = d.roll_id
    GROUP BY p.project_id
    ORDER BY p.archive_id
    """
    
    df = pd.read_sql_query(query, conn)
    
    # Format the data
    df['date_created'] = pd.to_datetime(df['date_created']).dt.strftime('%Y-%m-%d %H:%M')
    df['has_oversized'] = df['has_oversized'].map({1: 'Yes', 0: 'No'})
    
    # Fill NaN values
    df = df.fillna(0)
    
    # Convert numeric columns to int where appropriate
    numeric_cols = ['total_rolls', 'rolls_16mm', 'rolls_35mm', 'pages_16mm', 'pages_35mm', 'total_documents', 'documents_with_oversized']
    for col in numeric_cols:
        df[col] = df[col].astype(int)
    
    output_file = output_dir / "01_Projects_Overview.xlsx"
    df.to_excel(output_file, index=False, sheet_name='Projects Overview')
    print(f"✅ Generated: {output_file}")
    return output_file

def generate_rolls_report(conn, output_dir):
    """Generate detailed rolls report."""
    query = """
    SELECT 
        r.roll_id,
        r.film_number,
        r.film_type,
        p.archive_id,
        p.location,
        p.folderName as project_folder,
        r.capacity,
        r.pages_used,
        r.pages_remaining,
        ROUND((r.pages_used * 100.0 / r.capacity), 2) as utilization_percent,
        r.status,
        r.film_number_source,
        COUNT(d.document_id) as document_count,
        MIN(d.document_name) as first_document,
        MAX(d.document_name) as last_document,
        r.creation_date
    FROM Rolls r
    JOIN Projects p ON r.project_id = p.project_id
    LEFT JOIN Documents d ON r.roll_id = d.roll_id
    GROUP BY r.roll_id
    ORDER BY r.film_number
    """
    
    df = pd.read_sql_query(query, conn)
    
    # Format the data
    df['creation_date'] = pd.to_datetime(df['creation_date']).dt.strftime('%Y-%m-%d %H:%M')
    df = df.fillna('')
    
    output_file = output_dir / "02_Film_Rolls_Detail.xlsx"
    df.to_excel(output_file, index=False, sheet_name='Film Rolls')
    print(f"✅ Generated: {output_file}")
    return output_file

def generate_documents_report(conn, output_dir):
    """Generate detailed documents report."""
    query = """
    SELECT 
        d.document_id,
        d.document_name,
        d.com_id,
        p.archive_id,
        p.location,
        r.film_number,
        r.film_type,
        d.page_range_start,
        d.page_range_end,
        (d.page_range_end - d.page_range_start + 1) as page_count,
        d.is_oversized,
        d.blip,
        d.blipend,
        d.blip_type,
        p.folderName as project_folder
    FROM Documents d
    JOIN Rolls r ON d.roll_id = r.roll_id
    JOIN Projects p ON r.project_id = p.project_id
    ORDER BY r.film_number, d.document_name
    """
    
    df = pd.read_sql_query(query, conn)
    
    # Format the data
    df['is_oversized'] = df['is_oversized'].map({1: 'Yes', 0: 'No'})
    df = df.fillna('')
    
    output_file = output_dir / "03_Documents_Detail.xlsx"
    df.to_excel(output_file, index=False, sheet_name='Documents')
    print(f"✅ Generated: {output_file}")
    return output_file

def generate_statistics_report(conn, output_dir):
    """Generate statistics and summary report."""
    
    # Overall statistics
    stats_query = """
    SELECT 
        'Total Projects' as metric,
        COUNT(DISTINCT p.project_id) as value
    FROM Projects p
    
    UNION ALL
    
    SELECT 
        'Total Documents' as metric,
        COUNT(DISTINCT d.document_id) as value
    FROM Documents d
    
    UNION ALL
    
    SELECT 
        'Total Pages' as metric,
        SUM(p.total_pages) as value
    FROM Projects p
    
    UNION ALL
    
    SELECT 
        'Total Film Rolls' as metric,
        COUNT(DISTINCT r.roll_id) as value
    FROM Rolls r
    
    UNION ALL
    
    SELECT 
        'Projects with Oversized Pages' as metric,
        COUNT(DISTINCT p.project_id) as value
    FROM Projects p
    WHERE p.oversized = 1
    
    UNION ALL
    
    SELECT 
        'Total 16mm Rolls' as metric,
        COUNT(DISTINCT r.roll_id) as value
    FROM Rolls r
    WHERE r.film_type = '16mm'
    
    UNION ALL
    
    SELECT 
        'Total 35mm Rolls' as metric,
        COUNT(DISTINCT r.roll_id) as value
    FROM Rolls r
    WHERE r.film_type = '35mm'
    """
    
    stats_df = pd.read_sql_query(stats_query, conn)
    
    # Location breakdown
    location_query = """
    SELECT 
        p.location,
        COUNT(DISTINCT p.project_id) as projects,
        SUM(p.total_pages) as total_pages,
        COUNT(DISTINCT r.roll_id) as total_rolls,
        COUNT(DISTINCT d.document_id) as total_documents
    FROM Projects p
    LEFT JOIN Rolls r ON p.project_id = r.project_id
    LEFT JOIN Documents d ON r.roll_id = d.roll_id
    GROUP BY p.location
    ORDER BY p.location
    """
    
    location_df = pd.read_sql_query(location_query, conn)
    location_df = location_df.fillna(0)
    
    # Film type breakdown
    film_type_query = """
    SELECT 
        r.film_type,
        COUNT(DISTINCT r.roll_id) as rolls,
        SUM(r.pages_used) as pages_used,
        SUM(r.capacity) as total_capacity,
        ROUND(AVG(r.pages_used * 100.0 / r.capacity), 2) as avg_utilization
    FROM Rolls r
    GROUP BY r.film_type
    ORDER BY r.film_type
    """
    
    film_type_df = pd.read_sql_query(film_type_query, conn)
    film_type_df = film_type_df.fillna(0)
    
    # Write to Excel with multiple sheets
    output_file = output_dir / "04_Statistics_Summary.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        stats_df.to_excel(writer, sheet_name='Overall Statistics', index=False)
        location_df.to_excel(writer, sheet_name='By Location', index=False)
        film_type_df.to_excel(writer, sheet_name='By Film Type', index=False)
    
    print(f"✅ Generated: {output_file}")
    return output_file

def generate_film_numbers_report(conn, output_dir):
    """Generate film numbers allocation report."""
    query = """
    SELECT 
        r.film_number,
        r.film_type,
        p.archive_id,
        p.location,
        r.film_number_source,
        r.pages_used,
        r.capacity,
        r.pages_remaining,
        ROUND((r.pages_used * 100.0 / r.capacity), 2) as utilization_percent,
        COUNT(d.document_id) as document_count,
        r.creation_date
    FROM Rolls r
    JOIN Projects p ON r.project_id = p.project_id
    LEFT JOIN Documents d ON r.roll_id = d.roll_id
    GROUP BY r.roll_id
    ORDER BY r.film_number
    """
    
    df = pd.read_sql_query(query, conn)
    
    # Format the data
    df['creation_date'] = pd.to_datetime(df['creation_date']).dt.strftime('%Y-%m-%d %H:%M')
    df = df.fillna('')
    
    output_file = output_dir / "05_Film_Numbers_Allocation.xlsx"
    df.to_excel(output_file, index=False, sheet_name='Film Numbers')
    print(f"✅ Generated: {output_file}")
    return output_file

def main():
    """Main function to generate all Excel reports."""
    print("🎯 Microfilm Analysis Excel Report Generator")
    print("=" * 50)
    
    # Setup paths
    script_dir = Path(__file__).parent
    db_path = script_dir / "analysis_film_allocation.sqlite3"
    output_dir = script_dir / "Excel_Reports"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Check if database exists
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print("   Please run the analysis first to generate the database.")
        return 1
    
    # Connect to database
    conn = connect_to_database(db_path)
    if not conn:
        return 1
    
    try:
        print("\n🔄 Generating Excel reports...")
        
        # Generate all reports
        reports_generated = []
        
        reports_generated.append(generate_projects_report(conn, output_dir))
        reports_generated.append(generate_rolls_report(conn, output_dir))
        reports_generated.append(generate_documents_report(conn, output_dir))
        reports_generated.append(generate_statistics_report(conn, output_dir))
        reports_generated.append(generate_film_numbers_report(conn, output_dir))
        
        # Summary
        print(f"\n✅ Successfully generated {len(reports_generated)} Excel reports:")
        for report in reports_generated:
            print(f"   📊 {report.name}")
        
        print(f"\n📂 All reports saved to: {output_dir}")
        
        # Database statistics
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Projects")
        project_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Rolls")
        roll_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Documents")
        doc_count = cursor.fetchone()[0]
        
        print(f"\n📈 Database contains:")
        print(f"   • {project_count} projects")
        print(f"   • {roll_count} film rolls")
        print(f"   • {doc_count} documents")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating reports: {e}")
        return 1
    
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
