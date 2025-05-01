from flask import Flask, render_template, request, jsonify
import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import sys
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tuongrollsroyce'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# For server shutdown
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        # Flask >= 2.0
        import os
        os._exit(0)  # Force exit
    else:
        # Flask < 2.0
        func()
        
@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown the server"""
    shutdown_server()
    return jsonify({'success': True, 'message': 'Server shutting down...'})

# Global queue for passing dialog results
dialog_queue = queue.Queue()

def create_file_dialog(dialog_type, initial_dir=None):
    """Run a Tkinter file dialog in a separate thread and return the result"""
    def run_dialog():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Make sure the dialog appears on top
        root.attributes('-topmost', True)
        
        if dialog_type == 'folder':
            result = filedialog.askdirectory(initialdir=initial_dir)
        else:
            result = None
            
        dialog_queue.put(result)
        root.destroy()
    
    # Run Tkinter dialog in a separate thread to not block the Flask server
    dialog_thread = threading.Thread(target=run_dialog)
    dialog_thread.daemon = True
    dialog_thread.start()
    dialog_thread.join()  # Wait for dialog to complete
    
    # Get the result from the queue
    result = dialog_queue.get()
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/open_folder_dialog', methods=['POST'])
def open_folder_dialog():
    """Open a native folder picker dialog and return the selected path"""
    data = request.json
    initial_dir = data.get('initial_dir')
    
    # If no initial directory provided, use a reasonable default
    if not initial_dir or not os.path.isdir(initial_dir):
        if os.name == 'nt':  # Windows
            initial_dir = 'C:\\'
        else:  # Linux/Mac
            initial_dir = '/'
    
    selected_path = create_file_dialog('folder', initial_dir)
    
    if selected_path:
        # Normalize path for consistent handling
        selected_path = os.path.normpath(selected_path)
        return jsonify({
            'success': True,
            'path': selected_path
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No folder selected or dialog cancelled'
        })

@app.route('/get_files', methods=['POST'])
def get_files():
    data = request.json
    folder_path = data.get('folder_path')
    first_barcode = data.get('first_barcode', 1)
    
    # Handle Windows paths
    folder_path = os.path.normpath(folder_path)
    
    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'success': False, 'message': 'Invalid folder path'})
    
    files = []
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                files.append(filename)
        
        # Sort files alphabetically
        files.sort()
        
        # Map files to barcodes
        file_mappings = []
        current_barcode = int(first_barcode)
        
        for filename in files:
            ext = os.path.splitext(filename)[1]
            new_filename = f"{current_barcode}{ext}"
            file_mappings.append({
                'original': filename,
                'new': new_filename,
                'barcode': current_barcode
            })
            current_barcode += 1
            
        return jsonify({
            'success': True, 
            'files': file_mappings,
            'count': len(file_mappings)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/export_files', methods=['POST'])
def export_files():
    data = request.json
    source_folder = data.get('source_folder')
    target_folder = data.get('target_folder')
    file_mappings = data.get('file_mappings', [])
    
    # Handle Windows paths
    source_folder = os.path.normpath(source_folder)
    target_folder = os.path.normpath(target_folder)
    
    if not source_folder or not target_folder:
        return jsonify({'success': False, 'message': 'Invalid folder paths'})
    
    if not os.path.isdir(source_folder) or not os.path.isdir(target_folder):
        return jsonify({'success': False, 'message': 'Source or target folder does not exist'})
    
    try:
        copied_files = []
        errors = []
        
        for mapping in file_mappings:
            source_file = os.path.join(source_folder, mapping['original'])
            target_file = os.path.join(target_folder, mapping['new'])
            
            # Check if file exists
            if os.path.exists(source_file):
                try:
                    shutil.copy2(source_file, target_file)
                    copied_files.append(mapping)
                except Exception as e:
                    errors.append(f"Error copying {mapping['original']}: {str(e)}")
        
        if errors:
            return jsonify({
                'success': True,
                'message': f'Successfully exported {len(copied_files)} files with {len(errors)} errors',
                'exported_files': copied_files,
                'errors': errors
            })
        else:
            return jsonify({
                'success': True,
                'message': f'Successfully exported {len(copied_files)} files',
                'exported_files': copied_files
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/select_folder', methods=['POST'])
def select_folder():
    """
    Endpoint used for validating folder paths
    """
    try:
        folder_path = request.json.get('path')
        if not folder_path:
            return jsonify({'success': False, 'message': 'No path provided'})
        
        folder_path = os.path.normpath(folder_path)
        
        if not os.path.isdir(folder_path):
            return jsonify({'success': False, 'message': 'Invalid directory path'})
            
        return jsonify({
            'success': True,
            'path': folder_path
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/open_folder', methods=['POST'])
def open_folder():
    """
    Opens a folder in the system's file explorer
    """
    try:
        folder_path = request.json.get('folder_path')
        if not folder_path:
            return jsonify({'success': False, 'message': 'No path provided'})
        
        folder_path = os.path.normpath(folder_path)
        
        if not os.path.isdir(folder_path):
            return jsonify({'success': False, 'message': 'Invalid directory path'})
            
        # Open folder in the system's file explorer
        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':  # macOS
            import subprocess
            subprocess.call(['open', folder_path])
        else:  # Linux
            import subprocess
            subprocess.call(['xdg-open', folder_path])
            
        return jsonify({
            'success': True,
            'message': 'Folder opened successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error opening folder: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
