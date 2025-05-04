import os
import sys
from pathlib import Path

# ANSI color codes
COLORS = {
    'py': '\033[92m',     # Green
    'html': '\033[38;5;208m',  # Orange
    'css': '\033[94m',     # Blue
    'js': '\033[93m',      # Yellow
    'reset': '\033[0m',    # Reset
    'header': '\033[1;97m',  # Bold white for headers
    'total': '\033[1;95m'  # Bold magenta for totals
}

def get_file_stats(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            line_count = len(lines)
            char_count = sum(len(line) for line in lines)
        return line_count, char_count
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0, 0

def count_lines_and_chars_by_extension(directory):
    results = {
        'py': [],
        'html': [],
        'css': [],
        'js': []
    }

    try:
        base_path = Path(directory)
        for file_path in base_path.glob('**/*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()[1:]
                if ext in results:
                    line_count, char_count = get_file_stats(file_path)
                    results[ext].append((file_path.name, line_count, char_count))
    except Exception as e:
        print(f"Error scanning directory: {e}")
    
    return results

def print_table_header():
    print(f"{COLORS['header']}┌─{'─' * 15}┬─{'─' * 50}┬─{'─' * 10}┬─{'─' * 12}┐{COLORS['reset']}")
    print(f"{COLORS['header']}│ {'Extension':<15}│ {'File Name':<50}│ {'Lines':<10}│ {'Characters':<12}│{COLORS['reset']}")
    print(f"{COLORS['header']}├─{'─' * 15}┼─{'─' * 50}┼─{'─' * 10}┼─{'─' * 12}┤{COLORS['reset']}")

def print_table_footer():
    print(f"{COLORS['header']}└─{'─' * 15}┴─{'─' * 50}┴─{'─' * 10}┴─{'─' * 12}┘{COLORS['reset']}")

def print_table_separator():
    print(f"{COLORS['header']}├─{'─' * 15}┼─{'─' * 50}┼─{'─' * 10}┼─{'─' * 12}┤{COLORS['reset']}")

def print_results(results):
    total_files = sum(len(files) for files in results.values())
    if total_files == 0:
        print("No matching files found.")
        return

    print_table_header()

    grand_total_lines = 0
    grand_total_chars = 0
    extension_totals = {}

    for ext, files in results.items():
        if not files:
            continue

        files.sort(key=lambda x: x[0])
        total_lines = sum(line_count for _, line_count, _ in files)
        total_chars = sum(char_count for _, _, char_count in files)
        extension_totals[ext] = (len(files), total_lines, total_chars)

        grand_total_lines += total_lines
        grand_total_chars += total_chars

        for file_name, line_count, char_count in files:
            display_name = file_name if len(file_name) <= 48 else file_name[:47] + "…"
            print(f"{COLORS[ext]}│ {ext:<15}│ {display_name:<50}│ {line_count:<10}│ {char_count:<12}│{COLORS['reset']}")

        print_table_separator()
        print(f"{COLORS[ext]}│ {f'TOTAL {ext.upper()}':<15}│ {f'({len(files)} files)':<50}│ {total_lines:<10}│ {total_chars:<12}│{COLORS['reset']}")
        print_table_separator()

    print(f"{COLORS['total']}│ {'GRAND TOTAL':<15}│ {f'({total_files} files)':<50}│ {grand_total_lines:<10}│ {grand_total_chars:<12}│{COLORS['reset']}")
    print_table_footer()

    # Reprint summary totals for each extension
    print(f"\n{COLORS['header']}Summary Totals by File Type:{COLORS['reset']}")
    for ext, (count, lines, chars) in extension_totals.items():
        print(f"{COLORS[ext]}{ext.upper():<6}: {count} files, {lines} lines, {chars} chars{COLORS['reset']}")

if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    micro_dir = script_path.parent.parent.parent
    target_dir = micro_dir

    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])

    print(f"{COLORS['header']}Code Statistics{COLORS['reset']}")
    print(f"Scanning directory: {target_dir}\n")

    results = count_lines_and_chars_by_extension(target_dir)
    print_results(results)
