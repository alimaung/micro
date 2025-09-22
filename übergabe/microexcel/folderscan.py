# Find the best matching string to detect the document folder in a project folder

import re
import os
import json
import argparse
from collections import Counter
from pathlib import Path

def load_folder_names(filename):
    """Load folder names from export file, excluding summary lines"""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove summary lines and empty lines
    folder_names = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('Total'):
            folder_names.append(line)
    
    return folder_names

def test_patterns(folder_names, patterns):
    """Test patterns against folder names and show results"""
    results = {}
    
    for pattern_name, pattern in patterns.items():
        matches = []
        non_matches = []
        
        for folder in folder_names:
            if re.search(pattern, folder, re.IGNORECASE):
                matches.append(folder)
            else:
                non_matches.append(folder)
        
        results[pattern_name] = {
            'pattern': pattern,
            'matches': matches,
            'non_matches': non_matches,
            'match_count': len(matches),
            'total': len(folder_names),
            'percentage': (len(matches) / len(folder_names)) * 100
        }
    
    return results

def display_results(results):
    """Display test results with color coding"""
    print("=" * 80)
    print("PATTERN MATCHING RESULTS")
    print("=" * 80)
    
    for pattern_name, result in results.items():
        print(f"\n🔍 Pattern: {pattern_name}")
        print(f"   Regex: {result['pattern']}")
        print(f"   Matches: {result['match_count']}/{result['total']} ({result['percentage']:.1f}%)")
        
        # Show first 10 matches (green)
        print(f"\n   ✅ Matches (showing first 10):")
        for folder in result['matches'][:10]:
            print(f"      \033[92m{folder}\033[0m")
        if len(result['matches']) > 10:
            print(f"      ... and {len(result['matches']) - 10} more")
        
        # Show first 10 non-matches (red)
        print(f"\n   ❌ Non-matches (showing first 10):")
        for folder in result['non_matches'][:10]:
            print(f"      \033[91m{folder}\033[0m")
        if len(result['non_matches']) > 10:
            print(f"      ... and {len(result['non_matches']) - 10} more")
        
        print("-" * 60)

def analyze_folder_patterns(folder_names):
    """Analyze folder names to suggest good patterns"""
    print("\n📊 PATTERN ANALYSIS")
    print("=" * 50)
    
    # Count common words/patterns
    word_counts = Counter()
    for folder in folder_names:
        # Split by common separators and count words
        words = re.findall(r'\b\w+\b', folder.lower())
        word_counts.update(words)
    
    print("\n🔤 Most common words:")
    for word, count in word_counts.most_common(10):
        percentage = (count / len(folder_names)) * 100
        print(f"   {word}: {count} times ({percentage:.1f}%)")
    
    # Analyze patterns with "zu"
    zu_patterns = [f for f in folder_names if 'zu' in f.lower()]
    print(f"\n📁 Folders with 'zu': {len(zu_patterns)} ({(len(zu_patterns)/len(folder_names))*100:.1f}%)")
    
    # Analyze patterns with RRD codes
    rrd_patterns = [f for f in folder_names if re.search(r'RRD\d{3}-\d{4}', f)]
    print(f"📁 Folders with RRD codes: {len(rrd_patterns)} ({(len(rrd_patterns)/len(folder_names))*100:.1f}%)")

def check_pdf_files(root_path="X:/"):
    """Check actual PDF files in project subfolders"""
    if not os.path.exists(root_path):
        print(f"⚠️  Warning: Path {root_path} not accessible")
        return {}
    
    pdf_analysis = {}
    exclude_folders = {".management", "archive.ico", "autorun.inf", "$RECYCLE.BIN", "System Volume Information"}
    
    try:
        for item in os.listdir(root_path):
            if item in exclude_folders or not os.path.isdir(os.path.join(root_path, item)):
                continue
                
            project_path = os.path.join(root_path, item)
            
            try:
                for subfolder in os.listdir(project_path):
                    subfolder_path = os.path.join(project_path, subfolder)
                    
                    if os.path.isdir(subfolder_path) and not subfolder.startswith('.'):
                        # Count files
                        all_files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
                        pdf_files = [f for f in all_files if f.lower().endswith('.pdf')]
                        
                        pdf_analysis[subfolder] = {
                            'total_files': len(all_files),
                            'pdf_files': len(pdf_files),
                            'only_pdfs': len(pdf_files) == len(all_files) and len(all_files) > 0,
                            'has_pdfs': len(pdf_files) > 0
                        }
            except PermissionError:
                continue
                
    except Exception as e:
        print(f"⚠️  Error accessing {root_path}: {e}")
    
    return pdf_analysis

def export_results(results, pdf_data, filename, format_type):
    """Export results to file"""
    if format_type == 'json':
        export_data = {
            'pattern_results': results,
            'pdf_analysis': pdf_data,
            'summary': {
                'best_pattern': max(results.items(), key=lambda x: x[1]['match_count'])[0],
                'total_folders': len(load_folder_names('folderexport.txt'))
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    else:  # txt format
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("PATTERN MATCHING RESULTS\n")
            f.write("=" * 80 + "\n\n")
            
            for pattern_name, result in results.items():
                f.write(f"Pattern: {pattern_name}\n")
                f.write(f"Regex: {result['pattern']}\n")
                f.write(f"Matches: {result['match_count']}/{result['total']} ({result['percentage']:.1f}%)\n\n")
                
                f.write("Matches:\n")
                for folder in result['matches']:
                    f.write(f"  ✅ {folder}\n")
                
                f.write("\nNon-matches:\n")
                for folder in result['non_matches']:
                    f.write(f"  ❌ {folder}\n")
                
                f.write("\n" + "-" * 60 + "\n\n")
            
            if pdf_data:
                f.write("\nPDF FILE ANALYSIS\n")
                f.write("=" * 40 + "\n")
                for folder, data in pdf_data.items():
                    f.write(f"{folder}: {data['pdf_files']}/{data['total_files']} PDFs, Only PDFs: {data['only_pdfs']}\n")

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Analyze folder patterns for PDF detection")
    parser.add_argument("-p", "--pdf-check", action="store_true", help="Check actual PDF files in subfolders")
    parser.add_argument("-e", "--export-txt", type=str, nargs='?', const='folderscan_results.txt', help="Export to text file")
    parser.add_argument("-j", "--export-json", type=str, nargs='?', const='folderscan_results.json', help="Export to JSON file")
    args = parser.parse_args()
    
    # Load folder names from export file
    folder_names = load_folder_names('folderexport.txt')
    print(f"📂 Loaded {len(folder_names)} folder names from folderexport.txt")
    
    # Check PDF files if requested
    pdf_data = {}
    if args.pdf_check:
        print("\n🔍 Checking actual PDF files in subfolders...")
        pdf_data = check_pdf_files()
        
        print(f"\n📄 PDF FILE ANALYSIS")
        print("=" * 50)
        
        folders_with_pdfs = 0
        folders_only_pdfs = 0
        
        for folder, data in pdf_data.items():
            if data['has_pdfs']:
                folders_with_pdfs += 1
            if data['only_pdfs']:
                folders_only_pdfs += 1
            
            status = "📄" if data['only_pdfs'] else "📁" if data['has_pdfs'] else "❌"
            print(f"   {status} {folder}: {data['pdf_files']}/{data['total_files']} PDFs, Only PDFs: {data['only_pdfs']}")
        
        print(f"\n📊 Summary:")
        print(f"   Folders with PDFs: {folders_with_pdfs}/{len(pdf_data)} ({(folders_with_pdfs/len(pdf_data)*100):.1f}%)")
        print(f"   Folders with ONLY PDFs: {folders_only_pdfs}/{len(pdf_data)} ({(folders_only_pdfs/len(pdf_data)*100):.1f}%)")
    
    # Define test patterns
    patterns = {
        'PDF (simple)': r'pdf',
        'importiert': r'importiert',
        'PDF or importiert': r'(pdf|importiert)',
        'PDFs zu': r'pdfs?\s+zu',
        'PDF variations': r'p+d+f+s?',  # Handles PDF, pdf, PDFs, pDF, etc.
        'PDF with separators': r'pdf[s]?[\s_-]*(zu|zum|für|verfilmung)?',
        'Archive patterns': r'(pdf|importiert|zu|verfilmung)',
        'RRD codes': r'RRD\d{3}-\d{4}',  # Archive ID pattern from ProjectService
    }
    
    # Test patterns
    results = test_patterns(folder_names, patterns)
    
    # Display results
    display_results(results)
    
    # Analyze patterns
    analyze_folder_patterns(folder_names)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    best_pattern = max(results.items(), key=lambda x: x[1]['match_count'])
    print(f"🏆 Best pattern: {best_pattern[0]} ({best_pattern[1]['percentage']:.1f}% coverage)")
    
    print(f"\n💡 Recommendations:")
    print(f"   1. Use 'Archive patterns' for best string-based coverage")
    print(f"   2. ProjectService 3-tier strategy is still superior")
    print(f"   3. Content-based detection (Strategy 3) catches everything")
    
    # Export results
    if args.export_txt:
        export_results(results, pdf_data, args.export_txt, 'txt')
        print(f"\n📄 Results exported to: {args.export_txt}")
    
    if args.export_json:
        export_results(results, pdf_data, args.export_json, 'json')
        print(f"\n📄 Results exported to: {args.export_json}")

if __name__ == "__main__":
    main()