import os
import win32com.client
from pathlib import Path
import shutil
import csv
import json
from datetime import datetime
import pandas as pd

# Get the script's relative path
script_path = Path(__file__).parent
#root_path = script_path / "root"
root_path = r"\\Dehesdna-a009a\projekte\k-z\ofs\Archivierung\Mikroverfilmung_in_OU\Verfilmung_Oberursel_Übergabe" # DONT TOUCH THIS

def get_shortcut_target(lnk_path):
    """Get the target path of a .lnk shortcut file"""
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(lnk_path)
        return shortcut.Targetpath
    except Exception as e:
        print(f"Error reading shortcut {lnk_path}: {e}")
        return None

def should_exclude_path(path, root_dir):
    """Check if a path should be excluded based on .warteschlange or .abgeschlossen folders"""
    relative_path = os.path.relpath(path, root_dir)
    path_parts = relative_path.split(os.sep)
    
    # Check if any part of the path contains the excluded folders
    excluded_folders = {'.warteschlange', '.abgeschlossen'}
    
    for part in path_parts:
        if part in excluded_folders:
            return True
    
    return False

def find_all_shortcuts(root_dir):
    """Recursively find all .lnk files in the root directory, excluding .warteschlange and .abgeschlossen"""
    shortcuts = []
    
    try:
        for root, dirs, files in os.walk(root_dir):
            # Skip if current directory should be excluded
            if should_exclude_path(root, root_dir):
                continue
            
            # Remove excluded directories from dirs list to prevent os.walk from entering them
            dirs[:] = [d for d in dirs if not should_exclude_path(os.path.join(root, d), root_dir)]
            
            for file in files:
                if file.lower().endswith('.lnk'):
                    lnk_path = os.path.join(root, file)
                    
                    # Double-check that the file itself is not in an excluded path
                    if not should_exclude_path(lnk_path, root_dir):
                        relative_path = os.path.relpath(lnk_path, root_dir)
                        shortcuts.append({
                            'path': lnk_path,
                            'name': file,
                            'relative_path': relative_path
                        })
    except Exception as e:
        print(f"Error searching for shortcuts: {e}")
    
    return shortcuts

def get_target_folder_stats(target_path):
    """Get total size and PDF count for target folder"""
    total_size = 0
    pdf_count = 0
    
    try:
        if os.path.exists(target_path) and os.path.isdir(target_path):
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        if file.lower().endswith('.pdf'):
                            pdf_count += 1
                    except (OSError, FileNotFoundError):
                        continue
        elif os.path.exists(target_path) and os.path.isfile(target_path):
            # Handle case where shortcut points to a single file
            try:
                total_size = os.path.getsize(target_path)
                if target_path.lower().endswith('.pdf'):
                    pdf_count = 1
            except (OSError, FileNotFoundError):
                pass
    except Exception as e:
        print(f"Error analyzing target {target_path}: {e}")
    
    return total_size, pdf_count

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def create_size_bar(size, max_size, width=60):
    """Create a visual size bar"""
    if max_size == 0:
        return "▁" * width
    
    filled = int((size / max_size) * width)
    bar = "█" * filled + "▁" * (width - filled)
    return bar

def export_to_csv(targets, output_dir):
    """Export results to CSV format"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"shortcut_analysis_{timestamp}.csv"
    filepath = output_dir / filename
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Rank', 'Shortcut_Name', 'Target_Path', 'Source_Path', 
                'Size_Bytes', 'Size_Formatted', 'PDF_Count', 'Accessible', 
                'Percentage_of_Largest'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            max_size = max(target['size'] for target in targets) if targets else 0
            
            for i, target in enumerate(targets, 1):
                percentage = (target['size'] / max_size * 100) if max_size > 0 else 0
                writer.writerow({
                    'Rank': i,
                    'Shortcut_Name': target['shortcut_name'],
                    'Target_Path': target['target_path'],
                    'Source_Path': target['relative_path'],
                    'Size_Bytes': target['size'],
                    'Size_Formatted': format_size(target['size']),
                    'PDF_Count': target['pdfs'],
                    'Accessible': target['accessible'],
                    'Percentage_of_Largest': f"{percentage:.1f}%"
                })
        
        print(f"✅ CSV exported: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
        return None

def export_to_json(targets, output_dir, summary_stats):
    """Export results to JSON format"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"shortcut_analysis_{timestamp}.json"
    filepath = output_dir / filename
    
    try:
        max_size = max(target['size'] for target in targets) if targets else 0
        
        # Prepare data with additional metadata
        export_data = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "root_path": str(root_path),
                "excluded_folders": [".warteschlange", ".abgeschlossen"],
                "total_shortcuts_found": len(targets),
                "accessible_targets": summary_stats['accessible_count'],
                "total_size_bytes": summary_stats['total_size'],
                "total_size_formatted": format_size(summary_stats['total_size']),
                "total_pdf_files": summary_stats['total_pdfs']
            },
            "targets": []
        }
        
        for i, target in enumerate(targets, 1):
            percentage = (target['size'] / max_size * 100) if max_size > 0 else 0
            export_data["targets"].append({
                "rank": i,
                "shortcut_name": target['shortcut_name'],
                "target_path": target['target_path'],
                "source_path": target['relative_path'],
                "size_bytes": target['size'],
                "size_formatted": format_size(target['size']),
                "pdf_count": target['pdfs'],
                "accessible": target['accessible'],
                "percentage_of_largest": round(percentage, 1)
            })
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON exported: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error exporting JSON: {e}")
        return None

def export_to_excel(targets, output_dir, summary_stats):
    """Export results to Excel format with multiple sheets"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"shortcut_analysis_{timestamp}.xlsx"
    filepath = output_dir / filename
    
    try:
        # Prepare main data
        max_size = max(target['size'] for target in targets) if targets else 0
        
        main_data = []
        for i, target in enumerate(targets, 1):
            percentage = (target['size'] / max_size * 100) if max_size > 0 else 0
            main_data.append({
                'Rank': i,
                'Shortcut Name': target['shortcut_name'],
                'Target Path': target['target_path'],
                'Source Path': target['relative_path'],
                'Size (Bytes)': target['size'],
                'Size (Formatted)': format_size(target['size']),
                'PDF Count': target['pdfs'],
                'Accessible': target['accessible'],
                'Percentage of Largest': f"{percentage:.1f}%"
            })
        
        # Create summary data
        summary_data = [
            ['Analysis Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Root Path', str(root_path)],
            ['Excluded Folders', '.warteschlange, .abgeschlossen'],
            ['Total Shortcuts Found', len(targets)],
            ['Accessible Targets', summary_stats['accessible_count']],
            ['Total Size', format_size(summary_stats['total_size'])],
            ['Total PDF Files', summary_stats['total_pdfs']]
        ]
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main results sheet
            df_main = pd.DataFrame(main_data)
            df_main.to_excel(writer, sheet_name='Analysis Results', index=False)
            
            # Summary sheet
            df_summary = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format the sheets
            workbook = writer.book
            
            # Format main sheet
            worksheet_main = writer.sheets['Analysis Results']
            for column in worksheet_main.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet_main.column_dimensions[column_letter].width = adjusted_width
            
            # Format summary sheet
            worksheet_summary = writer.sheets['Summary']
            worksheet_summary.column_dimensions['A'].width = 25
            worksheet_summary.column_dimensions['B'].width = 50
        
        print(f"✅ Excel exported: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error exporting Excel: {e}")
        return None

def print_target_comparison(targets):
    """Print all target paths sorted by size"""
    if not targets:
        print("📭 No valid targets found")
        return
    
    # Find the largest size for relative comparison
    max_size = max(target['size'] for target in targets)
    terminal_width = shutil.get_terminal_size().columns
    bar_width = min(60, terminal_width - 50)  # Leave space for text
    
    print(f"\n🔍 Found {len(targets)} target paths, sorted by size:\n")
    
    for i, target in enumerate(targets, 1):
        # Size bar and percentage
        size_bar = create_size_bar(target['size'], max_size, bar_width)
        percentage = (target['size'] / max_size * 100) if max_size > 0 else 0
        
        # Shortcut name and target formatting
        shortcut_name = target['shortcut_name']
        if len(shortcut_name) > 30:
            shortcut_name = shortcut_name[:27] + "..."
        
        target_path = target['target_path']
        if len(target_path) > 50:
            target_path = "..." + target_path[-47:]
        
        # Size and PDF info
        size_str = format_size(target['size']).rjust(10)
        pdf_info = f" | {target['pdfs']} PDFs" if target['pdfs'] > 0 else ""
        
        # Status color
        if target['accessible']:
            color = "\033[92m"  # Green for accessible
        else:
            color = "\033[91m"  # Red for inaccessible
        
        print(f"{i:2d}. {color}{shortcut_name:<30}\033[0m")
        print(f"    Target: {target_path}")
        print(f"    {size_bar} {size_str} ({percentage:5.1f}%){pdf_info}")
        print(f"    Source: {target['relative_path']}")
        print()

def main():
    """Main function to analyze all shortcuts and compare target sizes"""
    print(f"\n\033[96m{'='*70}\033[0m")
    print(f"\033[96m🔍 SHORTCUT TARGET SIZE COMPARISON\033[0m")
    print(f"\033[96m📁 Root: {root_path}\033[0m")
    print(f"\033[96m🚫 Excluding: .warteschlange, .abgeschlossen folders\033[0m")
    print(f"\033[96m{'='*70}\033[0m")
    
    # Step 1: Find all shortcuts recursively (excluding specified folders)
    print("🔎 Searching for shortcuts...")
    shortcuts = find_all_shortcuts(root_path)
    print(f"   Found {len(shortcuts)} shortcut(s) (excluding .warteschlange/.abgeschlossen)")
    
    if not shortcuts:
        print("❌ No shortcuts found in the root directory")
        return
    
    # Step 2: Analyze each target path
    print("\n📊 Analyzing target paths...")
    targets = []
    
    for shortcut in shortcuts:
        print(f"   Processing: {shortcut['relative_path']}")
        
        target_path = get_shortcut_target(shortcut['path'])
        
        if target_path and os.path.exists(target_path):
            size, pdf_count = get_target_folder_stats(target_path)
            targets.append({
                'shortcut_name': shortcut['name'],
                'target_path': target_path,
                'relative_path': shortcut['relative_path'],
                'size': size,
                'pdfs': pdf_count,
                'accessible': True
            })
        else:
            targets.append({
                'shortcut_name': shortcut['name'],
                'target_path': target_path or "Unknown",
                'relative_path': shortcut['relative_path'],
                'size': 0,
                'pdfs': 0,
                'accessible': False
            })
    
    # Step 3: Sort by size (biggest to smallest) and display
    targets.sort(key=lambda x: x['size'], reverse=True)
    
    # Summary statistics
    total_size = sum(target['size'] for target in targets if target['accessible'])
    total_pdfs = sum(target['pdfs'] for target in targets if target['accessible'])
    accessible_count = sum(1 for target in targets if target['accessible'])
    
    summary_stats = {
        'total_size': total_size,
        'total_pdfs': total_pdfs,
        'accessible_count': accessible_count
    }
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total accessible targets: {accessible_count}/{len(targets)}")
    print(f"   Combined size: {format_size(total_size)}")
    print(f"   Total PDF files: {total_pdfs}")
    
    # Display comparison
    print_target_comparison(targets)
    
    # Export results
    if targets:
        print(f"\n📤 EXPORTING RESULTS:")
        output_dir = script_path / "exports"
        output_dir.mkdir(exist_ok=True)
        
        # Export to multiple formats
        export_to_csv(targets, output_dir)
        export_to_json(targets, output_dir, summary_stats)
        export_to_excel(targets, output_dir, summary_stats)
        
        print(f"\n📁 All exports saved to: {output_dir}")
    
    print(f"\n\033[92m✅ Analysis complete!\033[0m")
    print(f"\033[96m{'='*70}\033[0m")

if __name__ == "__main__":
    main()