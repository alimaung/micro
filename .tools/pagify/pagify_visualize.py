import json
import os
import datetime
import csv
from tabulate import tabulate
import tkinter as tk
from tkinter import filedialog, messagebox

JSON_FILE = "pagify_results.json"
CSV_OUTPUT = "pagify_results.csv"

def load_json_data(file_path=None):
    """Load data from the JSON file."""
    if not file_path:
        file_path = JSON_FILE
        
    if not os.path.exists(file_path):
        print(f"Error: JSON file not found at {file_path}")
        return None
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return None
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

def prepare_table_data(json_data):
    """Extract and prepare data for tabulation."""
    if not json_data:
        return []
        
    table_data = []
    
    for entry in json_data:
        # Handle both single directory and multiple directories format
        directories = entry.get("directories", [entry.get("directory", "Unknown")])
        
        # If directories is a string (old format), convert to list
        if isinstance(directories, str):
            directories = [directories]
            
        # Get other data
        timestamp = entry.get("timestamp", "Unknown")
        try:
            dt = datetime.datetime.fromisoformat(timestamp)
            timestamp = dt.strftime("%Y-%m-%d %H:%M")
        except:
            pass
            
        total_pages = entry.get("total_pages", 0)
        total_files = entry.get("total_pdf_files", 0)
        oversized_count = entry.get("oversized_pages_count", 0)
        rolls_needed = entry.get("rolls_needed", 0)
        
        # Create a row for each directory
        for directory in directories:
            table_data.append({
                "directory": os.path.basename(directory),
                "full_path": directory,
                "timestamp": timestamp,
                "total_files": total_files,
                "total_pages": total_pages,
                "oversized_count": oversized_count,
                "rolls_needed": rolls_needed
            })
    
    return table_data

def sort_table_data(table_data):
    """Sort the table data according to requirements:
    1. No oversized pages before oversized pages (PRIORITY)
    2. Then lowest page count
    3. Then by oversized count
    """
    return sorted(table_data, 
                  key=lambda x: (
                      x["oversized_count"] > 0,  # 1. No oversizes before oversizes (Priority)
                      x["total_pages"],          # 2. Sort by page count ascending
                      x["oversized_count"]       # 3. Sort by oversized count
                  ))

def display_table(table_data):
    """Format and display the data in a table."""
    if not table_data:
        print("No data to display.")
        return
        
    # Extract data for tabulate
    headers = ["Directory", "Path", "Date", "Files", "Pages", "Oversize", "Rolls"]
    rows = []
    
    for entry in table_data:
        rows.append([
            entry["directory"],
            entry["full_path"],
            entry["timestamp"],
            entry["total_files"],
            entry["total_pages"],
            entry["oversized_count"],
            f"{entry['rolls_needed']:.2f}"
        ])
    
    # Calculate totals
    total_files = sum(entry["total_files"] for entry in table_data)
    total_pages = sum(entry["total_pages"] for entry in table_data)
    total_oversized = sum(entry["oversized_count"] for entry in table_data)
    total_rolls = sum(entry["rolls_needed"] for entry in table_data)
    
    # Print the table
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    
    # Print the summary
    print("\nSummary:")
    print(f"Total Files: {total_files}")
    print(f"Total Pages: {total_pages}")
    print(f"Total Oversized Pages: {total_oversized}")
    print(f"Total Rolls Needed: {total_rolls:.2f}")

def export_to_csv(table_data, csv_file=CSV_OUTPUT):
    """Export the data to a CSV file"""
    if not table_data:
        print("No data to export.")
        return False
        
    headers = ["Directory", "Path", "Date", "Files", "Pages", "Oversize", "Rolls"]
    
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(headers)
            
            # Write data rows
            for entry in table_data:
                writer.writerow([
                    entry["directory"],
                    entry["full_path"],
                    entry["timestamp"],
                    entry["total_files"],
                    entry["total_pages"],
                    entry["oversized_count"],
                    f"{entry['rolls_needed']:.2f}"
                ])
            
            # Calculate totals
            total_files = sum(entry["total_files"] for entry in table_data)
            total_pages = sum(entry["total_pages"] for entry in table_data)
            total_oversized = sum(entry["oversized_count"] for entry in table_data)
            total_rolls = sum(entry["rolls_needed"] for entry in table_data)
            
            # Add blank row and totals
            writer.writerow([])
            writer.writerow(["TOTALS", "", "", 
                            total_files, 
                            total_pages, 
                            total_oversized, 
                            f"{total_rolls:.2f}"])
                            
        print(f"Data exported to {csv_file}")
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")
        return False

def main():
    root = tk.Tk()
    root.withdraw()
    
    # Ask if user wants to use a specific JSON file
    use_custom_file = messagebox.askyesno("JSON File Selection", 
                                         "Do you want to select a specific JSON file?\n(Default is pagify_results.json)")
    
    json_file = JSON_FILE
    if use_custom_file:
        json_file = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json")]
        )
        if not json_file:
            print("No file selected. Using default.")
            json_file = JSON_FILE
    
    # Load and process the data
    json_data = load_json_data(json_file)
    if json_data:
        table_data = prepare_table_data(json_data)
        sorted_data = sort_table_data(table_data)
        
        # Ask user if they want to display table, export to CSV, or both
        choice = messagebox.askyesnocancel("Output Options", 
                                          "Display table in console?\n\n"
                                          "Yes = Show table and export CSV\n"
                                          "No = Export CSV only\n"
                                          "Cancel = Show table only")
        
        if choice is not None:  # Not canceled
            if choice:  # Yes - show table and export
                display_table(sorted_data)
                export_to_csv(sorted_data)
            else:  # No - export only
                export_csv_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")],
                    title="Save CSV As"
                )
                if export_csv_path:
                    export_to_csv(sorted_data, export_csv_path)
                else:
                    export_to_csv(sorted_data)  # Use default
        else:  # Canceled - show table only
            display_table(sorted_data)
    
    # For GUI environment - wait for user input before closing
    if not os.isatty(0):  # 0 is stdin file descriptor
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 