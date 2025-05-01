import os
import shutil
import subprocess
import math
from PyPDF2 import PdfReader  # Updated from PdfFileReader to PdfReader (newer version)
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

def get_directory_info():
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(tool_dir)
    target_dir = os.path.join(root_dir, "target")
    
    root_folders = [folder for folder in os.listdir(root_dir) 
                    if os.path.isdir(os.path.join(root_dir, folder)) 
                    and folder != os.path.basename(tool_dir)
                    and folder != os.path.basename(target_dir)]

    ou_folder = [folder for folder in root_folders if "Übergabe_aus_OU" in folder]
    dw_folder = [folder for folder in root_folders if "Übergabe_aus_DW" in folder]
    
    ou_folders = []
    if ou_folder:
        ou_path = os.path.join(root_dir, ou_folder[0])
        # Filter out folders that start with a dot (.)
        ou_folders = [folder for folder in os.listdir(ou_path) 
                     if os.path.isdir(os.path.join(ou_path, folder)) and not folder.startswith('.')]
    
    dw_folders = []
    if dw_folder:
        dw_path = os.path.join(root_dir, dw_folder[0])
        # Filter out folders that start with a dot (.)
        dw_folders = [folder for folder in os.listdir(dw_path) 
                     if os.path.isdir(os.path.join(dw_path, folder)) and not folder.startswith('.')]

    return {
        "ou_folder": ou_folder[0] if ou_folder else "",
        "ou_folders": ou_folders,
        "dw_folder": dw_folder[0] if dw_folder else "",
        "dw_folders": dw_folders,
        "target_dir": target_dir,
        "root_dir": root_dir
    }

def copy_folders_to_target(selected_folders, target_dir, folder_type):
    """Copy the selected folders to the target directory and rename the original folders."""
    directory_info = get_directory_info()
    root_dir = directory_info["root_dir"] 
    
    results = []
    
    # Handle both single folder and list of folders
    if not isinstance(selected_folders, list):
        selected_folders = [selected_folders]
    
    for selected_folder in selected_folders:
        # Determine the correct source path based on the folder type
        if folder_type == "OU":
            source_path = os.path.join(root_dir, directory_info["ou_folder"], selected_folder)
        else:  # DW
            source_path = os.path.join(root_dir, directory_info["dw_folder"], selected_folder)

        destination_path = os.path.join(target_dir, selected_folder)

        # Check if the source path exists
        if not os.path.exists(source_path):
            results.append({"folder": selected_folder, "success": False, "message": f"Source folder does not exist: {source_path}"})
            continue

        # Copy the folder
        try:
            shutil.copytree(source_path, destination_path)
            
            # Rename the original folder by adding a '.' prefix
            new_name = f".{selected_folder}"
            new_source_path = os.path.join(os.path.dirname(source_path), new_name)
            os.rename(source_path, new_source_path)
            
            results.append({
                "folder": selected_folder, 
                "success": True, 
                "message": f"Successfully copied {selected_folder} to target and renamed original.", 
                "destination_path": destination_path
            })
        except Exception as e:
            results.append({"folder": selected_folder, "success": False, "message": f"Error during copy operation: {str(e)}"})
    
    # Determine overall success
    all_success = all(result["success"] for result in results)
    
    # Combine information for the response
    if len(results) == 1:
        # Single folder case - keep backward compatibility
        response = results[0]
        response["success"] = all_success
        return response
    else:
        # Multiple folders case
        successful_folders = [result["folder"] for result in results if result["success"]]
        failed_folders = [result["folder"] for result in results if not result["success"]]
        
        if all_success:
            message = f"Successfully copied {len(successful_folders)} folders to target and renamed originals."
        elif len(successful_folders) > 0:
            message = f"Partially successful: {len(successful_folders)} folders copied, {len(failed_folders)} failed."
        else:
            message = f"Failed to copy all {len(failed_folders)} folders."
            
        return {
            "success": all_success,
            "message": message,
            "details": results,
            "successful_folders": successful_folders,
            "failed_folders": failed_folders,
            "destination_path": target_dir  # Return the target directory for opening
        }

def open_folder_in_explorer(folder_path):
    """Open the specified folder in the file explorer."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
            return {"success": True}
    except Exception as e:
        return {"success": False, "message": f"Error opening folder: {str(e)}"}

@app.route('/transfer')
def index():
    directory_info = get_directory_info()
    return render_template('transfer.html', 
                           ou_folders=directory_info["ou_folders"],
                           dw_folders=directory_info["dw_folders"],
                           default_target=directory_info["target_dir"])

@app.route('/get_folders/<folder_type>')
def get_folders(folder_type):
    directory_info = get_directory_info()
    
    # Get the appropriate folders based on the folder type
    if folder_type == "OU":
        folders = directory_info["ou_folders"]
    else:
        folders = directory_info["dw_folders"]
    
    # Additional safety check to ensure no hidden folders are included
    folders = [folder for folder in folders if not folder.startswith('.')]
    
    return jsonify(folders)

@app.route('/transfer', methods=['POST'])
def transfer():
    folder_type = request.form.get('folder_type')
    selected_folders = request.form.getlist('selected_folders[]')  # Get list of selected folders
    target_path = request.form.get('target_path')
    
    # If no folders are selected, return an error
    if not selected_folders:
        return jsonify({"success": False, "message": "No folders selected."})
    
    result = copy_folders_to_target(selected_folders, target_path, folder_type)
    return jsonify(result)

@app.route('/open_folder', methods=['POST'])
def open_folder():
    """Endpoint to open a folder in the file explorer."""
    folder_path = request.form.get('path')
    if not folder_path:
        return jsonify({"success": False, "message": "No path provided"})
    
    result = open_folder_in_explorer(folder_path)
    return jsonify(result)

@app.route('/check_path', methods=['POST'])
def check_path():
    path = request.form.get('path')
    if os.path.exists(path) and os.path.isdir(path):
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})

@app.route('/browse_folder', methods=['GET'])
def browse_folder():
    """Open a folder picker dialog and return the selected path."""
    try:
        # For Windows and macOS
        if os.name == 'nt' or os.name == 'posix':
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                # Initialize tkinter properly
                root = tk.Tk()
                root.attributes('-topmost', True)  # Bring window to front
                root.withdraw()  # Hide the root window
                
                # Force focus (helps on some systems)
                root.focus_force()
                
                # Set initial directory based on OS
                if os.name == 'nt':  # Windows
                    # For Windows, None or empty string will show "This PC" view
                    initial_dir = '::{20D04FE0-3AEA-1069-A2D8-08002B30309D}'
                
                # Open the folder picker dialog with initial directory set
                folder_path = filedialog.askdirectory(initialdir=initial_dir)
                
                # Clean up
                root.destroy()
                
                if folder_path:
                    print(f"Selected folder: {folder_path}")
                    return jsonify({"path": folder_path})
                else:
                    return jsonify({"path": "", "message": "No folder selected"})
            except Exception as tk_error:
                # Fallback for systems without tkinter
                return jsonify({"error": f"Tkinter error: {str(tk_error)}", "path": ""})
            
    except Exception as e:
        return jsonify({"error": str(e), "path": ""})

# New function for PDF page counting and oversized detection
def get_total_pdf_pages(directory):
    """
    Counts the total number of pages in all PDF files in a directory
    and identifies pages that exceed A3 size with a specified threshold.
    
    Args:
        directory (str): Path to the directory containing PDF files
        
    Returns:
        tuple: (total_pdf_files, total_pages, oversized_pages, oversized_files_info)
            - total_pdf_files: Total number of PDF files found in the directory
            - total_pages: Total number of pages across all PDFs
            - oversized_pages: Number of pages exceeding the A3 threshold
            - oversized_files_info: List of tuples with (filename, page_number, dimensions)
    """
    total_pdf_files = 0
    total_pages = 0
    oversized_pages = 0
    oversized_files_info = []
    
    # A3 dimensions in points
    A3_SIZE_PORTRAIT = (842, 1191)  # A3 size in points (portrait)
    A3_SIZE_LANDSCAPE = (1191, 842)  # A3 size in points (landscape)
    THRESHOLD = 300  # Threshold in points
    
    # Paper sizes dictionary for comparison (copied from pagify.py)
    PAPER_SIZES = {
        'A0': (2384, 3370),
        'A1': (1684, 2384),
        'A2': (1191, 1684),
        'A3': (842, 1191),
        'A4': (595, 842),
        'A5': (420, 595),
        'A6': (297, 420),
        'Letter': (612, 792),
        'Legal': (612, 1008),
        'Tabloid': (792, 1224)
    }
    
    # Function to get closest paper size (based on pagify.py)
    def get_closest_paper_size(size, tolerance=300):
        best_match = "Unknown"
        smallest_difference = float("inf")
        
        for sizes, (w, h) in PAPER_SIZES.items():
            # Calculate Euclidean distance
            diff = math.sqrt((size[0] - w) ** 2 + (size[1] - h) ** 2)
            flipped_diff = math.sqrt((size[0] - h) ** 2 + (size[1] - w) ** 2)  # Account for rotation
            
            min_diff = min(diff, flipped_diff)
            
            if min_diff < smallest_difference:
                smallest_difference = min_diff
                best_match = sizes
                
        if smallest_difference <= tolerance:
            return best_match, smallest_difference
        return "Unknown", smallest_difference
    
    try:
        # Iterate through all files in the directory
        for filename in os.listdir(directory):
            if filename.lower().endswith('.pdf'):
                total_pdf_files += 1  # Count each PDF file
                file_path = os.path.join(directory, filename)
                
                try:
                    # Open the PDF file
                    with open(file_path, 'rb') as file:
                        pdf = PdfReader(file)
                        file_page_count = len(pdf.pages)
                        total_pages += file_page_count
                        
                        # Check each page for oversized dimensions
                        for page_num in range(file_page_count):
                            page = pdf.pages[page_num]
                            width = float(page.mediabox.width)
                            height = float(page.mediabox.height)
                            
                            # Get closest paper size
                            paper_size, diff = get_closest_paper_size((width, height))
                            
                            # If the paper size is larger than A3, it's oversized
                            if paper_size not in ["A3", "A4", "A5", "A6", "Letter", "Legal"]:
                                oversized_pages += 1
                                oversized_files_info.append((filename, page_num + 1, (width, height), paper_size))
                                
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    continue
                    
    except Exception as e:
        print(f"Error accessing directory {directory}: {str(e)}")
        return 0, 0, 0, []
        
    return total_pdf_files, total_pages, oversized_pages, oversized_files_info

@app.route('/pdf_pages', methods=['POST'])
def pdf_pages():
    """
    Endpoint to count PDF pages and detect oversized pages in a directory.
    Expects a 'directory' field in the POST request.
    """
    directory = request.form.get('directory')
    print(f"Directory: {directory}")
    
    if not directory:
        return jsonify({"success": False, "message": "No directory provided"})
    
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return jsonify({"success": False, "message": "Invalid directory path"})
    
    total_pdf_files, total_pages, oversized_pages, oversized_files_info = get_total_pdf_pages(directory)
    
    oversized_files = [
        {
            "filename": info[0], 
            "page_number": info[1], 
            "dimensions": f"{info[2][0]:.0f}x{info[2][1]:.0f}", 
            "paper_size": info[3]
        } 
        for info in oversized_files_info
    ]
    
    return jsonify({
        "success": True,
        "total_pages": total_pages,
        "oversized_pages": oversized_pages,
        "oversized_files": oversized_files,
        "total_pdf_files": total_pdf_files
    })

@app.route('/pdf_pages/<path:directory>', methods=['GET'])
def pdf_pages_path(directory):
    """
    Endpoint to count PDF pages and detect oversized pages in a directory.
    Takes the directory path directly in the URL.
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return jsonify({"success": False, "message": "Invalid directory path"})
    
    total_pdf_files, total_pages, oversized_pages, oversized_files_info = get_total_pdf_pages(directory)
    
    oversized_files = [
        {
            "filename": info[0], 
            "page_number": info[1], 
            "dimensions": f"{info[2][0]:.0f}x{info[2][1]:.0f}", 
            "paper_size": info[3]
        } 
        for info in oversized_files_info
    ]
    
    return jsonify({
        "success": True,
        "total_pages": total_pages,
        "oversized_pages": oversized_pages,
        "oversized_files": oversized_files,
        "total_pdf_files": total_pdf_files
    })

@app.route('/analysis')
def analysis():
    """
    Renders the analysis page for PDF page counting and oversized detection.
    """
    return render_template('analysis.html')

@app.route('/rename')
def rename():
    """
    Renders the rename page for file renaming functionality.
    """
    return render_template('rename.html')

@app.route('/get_files', methods=['POST'])
def get_files():
    """
    Endpoint to get the list of files in a directory.
    """
    directory_path = request.form.get('directory_path')
    
    if not directory_path:
        return jsonify({"error": "No directory provided"})
    
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return jsonify({"error": "Invalid directory path"})
    
    try:
        file_list = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                file_list.append({
                    "name": filename
                })
        
        return jsonify({
            "files": file_list,
            "count": len(file_list)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/rename_files', methods=['POST'])
def rename_files():
    """
    Endpoint to rename files in a directory.
    Files will always be copied to the target directory with new names (or to a subfolder in the original directory)
    to preserve the original files.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"})
        
        directory_path = data.get('directory_path')
        target_path = data.get('target_path', '')
        files = data.get('files', [])
        
        if not directory_path:
            return jsonify({"error": "No directory path provided"})
            
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return jsonify({"error": "Invalid directory path"})
            
        if not files:
            return jsonify({"error": "No files to rename"})
        
        # If no target path is provided, create a "renamed" subdirectory in the original directory
        if not target_path:
            target_path = os.path.join(directory_path, "renamed")
        
        # Check if target directory exists
        if not os.path.exists(target_path):
            try:
                os.makedirs(target_path)
            except Exception as e:
                return jsonify({"error": f"Could not create target directory: {str(e)}"})
        
        # Check if target directory is valid
        if not os.path.isdir(target_path):
            return jsonify({"error": "Target path is not a directory"})
        
        renamed_count = 0
        errors = []
        
        for file_mapping in files:
            original_name = file_mapping.get('original_name')
            new_name = file_mapping.get('new_name')
            
            if not original_name or not new_name:
                continue
                
            original_path = os.path.join(directory_path, original_name)
            
            # Always copy files to the target directory with the new name
            new_path = os.path.join(target_path, new_name)
            
            if os.path.exists(original_path):
                try:
                    if not os.path.exists(new_path):
                        shutil.copy2(original_path, new_path)
                        renamed_count += 1
                    else:
                        errors.append(f"File already exists in target directory: {new_name}")
                except Exception as e:
                    errors.append(f"Error copying {original_name}: {str(e)}")
        
        if errors:
            return jsonify({
                "success": True,
                "renamed_count": renamed_count,
                "errors": errors
            })
        else:
            return jsonify({
                "success": True,
                "renamed_count": renamed_count
            })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/generate_preview', methods=['POST'])
def generate_preview():
    """
    Endpoint to generate a preview of renamed files based on pattern.
    """
    try:
        files = request.form.getlist('files[]')
        pattern = request.form.get('pattern', '{num}')
        start_number = int(request.form.get('start_number', 1))
        
        if not files:
            return jsonify({"success": False, "message": "No files provided"})
        
        file_mappings = []
        for i, filename in enumerate(files):
            file_ext = os.path.splitext(filename)[1]  # Get file extension
            
            # Generate new filename using pattern
            new_filename = pattern.replace('{num}', str(start_number + i))
            # Add extension if not already in the pattern
            if not new_filename.endswith(file_ext):
                new_filename += file_ext
                
            file_mappings.append({
                "original": filename,
                "new": new_filename
            })
        
        return jsonify({
            "success": True, 
            "file_mappings": file_mappings
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 