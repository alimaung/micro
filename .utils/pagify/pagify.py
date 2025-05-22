import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import PyPDF2
import glob
import json
import datetime
from decimal import Decimal

# Constants
PAGES_PER_ROLL = 2900
A3_WIDTH_POINTS = 842
A3_HEIGHT_POINTS = 1191
JSON_OUTPUT_FILE = "pagify_results.json"

def select_directories():
    """Opens a dialog with a list of all folders in X: drive to select from"""
    root = tk.Tk()
    root.title("Select Folders to Scan")
    root.geometry("600x500")
    
    # Variable to track selected directories
    selected_dirs = []
    
    # Frame for instructions
    instruction_frame = tk.Frame(root)
    instruction_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(instruction_frame, text="Select folders to scan (hold Ctrl to select multiple):", 
             anchor="w").pack(fill=tk.X)
    
    # Create a frame for the listbox and scrollbar
    list_frame = tk.Frame(root)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Add scrollbars
    y_scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
    y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    x_scrollbar = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
    x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Create a listbox with all folders from X: drive
    folder_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, 
                               yscrollcommand=y_scrollbar.set,
                               xscrollcommand=x_scrollbar.set,
                               width=80, height=20)
    folder_listbox.pack(fill=tk.BOTH, expand=True)
    
    # Connect scrollbars to the listbox
    y_scrollbar.config(command=folder_listbox.yview)
    x_scrollbar.config(command=folder_listbox.xview)
    
    # Status label
    status_label = tk.Label(root, text="Loading folders from X: drive...", anchor="w")
    status_label.pack(fill=tk.X, padx=10, pady=5)
    
    # Button frame
    button_frame = tk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Load folders from X: drive
    try:
        # Get all folders in X: drive
        drive_path = "X:/"
        if os.path.exists(drive_path):
            all_folders = []
            for item in os.listdir(drive_path):
                item_path = os.path.join(drive_path, item)
                if os.path.isdir(item_path):
                    all_folders.append(item_path)
            
            # Update the listbox
            for folder in sorted(all_folders):
                folder_listbox.insert(tk.END, folder)
            
            status_label.config(text=f"Found {len(all_folders)} folders. Select folders to scan.")
        else:
            status_label.config(text="Error: X: drive not found or not accessible.")
            
    except Exception as e:
        status_label.config(text=f"Error loading folders: {str(e)}")
    
    # Functions for button actions
    def confirm_selection():
        selected_indices = folder_listbox.curselection()
        nonlocal selected_dirs
        selected_dirs = [folder_listbox.get(i) for i in selected_indices]
        root.quit()
    
    def cancel_selection():
        nonlocal selected_dirs
        selected_dirs = []
        root.quit()
    
    # Create buttons
    confirm_button = tk.Button(button_frame, text="Process Selected Folders", command=confirm_selection)
    confirm_button.pack(side=tk.RIGHT, padx=5)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_selection)
    cancel_button.pack(side=tk.RIGHT, padx=5)
    
    # Start the main event loop
    root.mainloop()
    
    # Destroy the window after mainloop ends
    root.destroy()
    
    return selected_dirs

def scan_pdf_files(directories):
    """Scan all PDF files in the selected directories"""
    if not directories:
        return []
    
    pdf_files = []
    
    for directory in directories:
        pdf_pattern = os.path.join(directory, "**/*.pdf")
        pdf_files.extend(glob.glob(pdf_pattern, recursive=True))
    
    return pdf_files

def analyze_pdfs(pdf_files):
    """Analyze PDF files to count pages and detect oversized pages"""
    total_pages = 0
    oversized_pages = []
    
    for pdf_file in pdf_files:
        try:
            with open(pdf_file, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                file_page_count = len(pdf_reader.pages)
                total_pages += file_page_count
                
                # Check each page size
                for page_num in range(file_page_count):
                    page = pdf_reader.pages[page_num]
                    width = page.mediabox.width
                    height = page.mediabox.height
                    
                    # Check if page is larger than A3
                    if width > A3_WIDTH_POINTS or height > A3_HEIGHT_POINTS:
                        oversized_pages.append({
                            'file': pdf_file,
                            'page': page_num + 1,
                            'width': float(width),  # Convert to float for JSON serialization
                            'height': float(height)  # Convert to float for JSON serialization
                        })
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    return total_pages, oversized_pages

def calculate_rolls(total_pages):
    """Calculate number of rolls needed"""
    rolls = total_pages / PAGES_PER_ROLL
    return rolls

def convert_decimal_values(obj):
    """Recursively convert any Decimal values to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_values(item) for item in obj]
    else:
        return obj

def save_to_json(directories, total_files, total_pages, oversized_pages, rolls_needed):
    """Save the results to a JSON file, appending to existing file if it exists"""
    # Create a data structure to save
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "directories": directories,
        "total_pdf_files": total_files,
        "total_pages": total_pages,
        "oversized_pages_count": len(oversized_pages),
        "rolls_needed": float(rolls_needed),  # Convert to float for JSON serialization
        "oversized_pages_details": oversized_pages
    }
    
    # Convert any Decimal values to float for JSON serialization
    data = convert_decimal_values(data)
    
    # Check if file exists and load existing data
    existing_data = []
    if os.path.exists(JSON_OUTPUT_FILE):
        try:
            with open(JSON_OUTPUT_FILE, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Existing file {JSON_OUTPUT_FILE} is not valid JSON. Creating new file.")
    
    # Append new data
    if isinstance(existing_data, list):
        existing_data.append(data)
    else:
        existing_data = [data]
    
    # Save combined data
    with open(JSON_OUTPUT_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2)
    
    print(f"Results saved to {JSON_OUTPUT_FILE}")

def main():
    # Step 1: Select directories
    directories = select_directories()
    if not directories:
        print("No directories selected. Exiting.")
        return
    
    print(f"Selected {len(directories)} directories for scanning.")
    
    # Process each selected directory individually
    all_results = []
    
    for directory in directories:
        print(f"\nProcessing folder: {directory}")
        
        # Step 2: Scan all PDF files in this directory
        pdf_files = scan_pdf_files([directory])  # Pass as list for the scan_pdf_files function
        print(f"Found {len(pdf_files)} PDF files in {directory}")
        
        if not pdf_files:
            print("No PDF files found. Skipping this directory.")
            continue
        
        # Step 3: Count pages and detect oversized pages
        total_pages, oversized_pages = analyze_pdfs(pdf_files)
        
        # Step 4: Calculate rolls
        rolls_needed = calculate_rolls(total_pages)
        
        # Display results
        result = f"""
PDF Analysis Results for {directory}:
--------------------
Total PDF files: {len(pdf_files)}
Total pages: {total_pages}
Oversized pages (bigger than A3): {len(oversized_pages)}
Rolls needed (1 roll = 2900 pages): {rolls_needed:.2f}
"""
        print(result)
        
        # Display oversized pages if any
        if oversized_pages:
            print("\nOversized Pages Details:")
            print("------------------------")
            for item in oversized_pages:
                print(f"File: {item['file']}")
                print(f"Page: {item['page']}")
                print(f"Size: {item['width']} x {item['height']} points")
                print("------------------------")
        
        # Save results to JSON file
        save_to_json([directory], len(pdf_files), total_pages, oversized_pages, rolls_needed)
        
        # Store the results for this directory
        all_results.append({
            "directory": directory,
            "total_files": len(pdf_files),
            "total_pages": total_pages,
            "oversized_count": len(oversized_pages),
            "rolls_needed": float(rolls_needed)
        })
    
    # Display summary of all processed directories
    if all_results:
        total_all_pages = sum(result["total_pages"] for result in all_results)
        total_all_rolls = sum(result["rolls_needed"] for result in all_results)
        total_all_files = sum(result["total_files"] for result in all_results)
        total_all_oversized = sum(result["oversized_count"] for result in all_results)
        
        print("\n" + "="*50)
        print("SUMMARY OF ALL PROCESSED DIRECTORIES")
        print("="*50)
        print(f"Total directories processed: {len(all_results)}")
        print(f"Total PDF files: {total_all_files}")
        print(f"Total pages: {total_all_pages}")
        print(f"Total oversized pages: {total_all_oversized}")
        print(f"Total rolls needed: {total_all_rolls:.2f}")
        print("="*50)

if __name__ == "__main__":
    main()
