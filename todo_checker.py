#!/usr/bin/env python3

import os
import re
import time
from pathlib import Path
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("todo.log"),
        logging.StreamHandler()
    ]
)

# Configuration
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
TODO_FILE = Path("C:/Users/Ali/Desktop/micro/TODO.md")
DONE_FILE = Path("C:/Users/Ali/Desktop/micro/TODONE.md")
FILE_EXTENSIONS = ['.html', '.js', '.css', '.py']

# Language-specific comment patterns
TODO_PATTERNS = {
    '.py': re.compile(r'(.*?[#]\s*)(TODO)x(\d*)(:[ \t]*)(.*?)($)'),
    '.js': re.compile(r'(.*?[/]{2}\s*)(TODO)x(\d*)(:[ \t]*)(.*?)($)'),
    '.css': re.compile(r'(.*?[/][*].*?)(TODO)x(\d*)(:[ \t]*)(.*?)([*][/].*)'),
    '.html': re.compile(r'(.*?<!--\s*)(TODO)x(\d*)(:[ \t]*)(.*?)(\s*-->.*)')
}

# Fallback pattern for any file type
DEFAULT_TODO_PATTERN = re.compile(r'(.*?)(TODO)x(\d*)(:[ \t]*)(.*?)($)')

CHECK_INTERVAL = 600  # 10 minutes in seconds

# Store tracked TODOs
tracked_todos = {}  # {id: {"file": file_path, "line": line_num, "content": todo_content}}
next_todo_id = 1

def initialize_logging():
    """Initialize the logging configuration."""
    # We already set up logging at the module level,
    # this function exists in case we need to reconfigure logging in the future
    logging.info("Logging initialized")

def load_config():
    """Load configuration settings from environment or config file if available."""
    global PROJECT_ROOT, TODO_FILE, FILE_EXTENSIONS, CHECK_INTERVAL
    
    # Could be extended to load from a config file or environment variables
    logging.info(f"Configuration loaded: PROJECT_ROOT={PROJECT_ROOT}, TODO_FILE={TODO_FILE}")
    logging.info(f"Monitoring extensions: {FILE_EXTENSIONS}")
    logging.info(f"Check interval: {CHECK_INTERVAL/60} minutes")

def find_files():
    """Find all relevant files in the project."""
    files = []
    for ext in FILE_EXTENSIONS:
        files.extend(PROJECT_ROOT.glob(f'**/*{ext}'))
    return files

def get_todo_pattern(file_path):
    """Get the appropriate TODO pattern based on file extension."""
    ext = file_path.suffix.lower()
    return TODO_PATTERNS.get(ext, DEFAULT_TODO_PATTERN)

def extract_todos_from_file(file_path):
    """Extract TODOs from a file and return a list of (line_num, line_content, todo_match)."""
    todos = []
    pattern = get_todo_pattern(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f, 1):
                match = pattern.search(line)
                if match:
                    todos.append((i, line, match))
                # Also try default pattern as fallback
                elif pattern != DEFAULT_TODO_PATTERN:
                    match = DEFAULT_TODO_PATTERN.search(line)
                    if match:
                        todos.append((i, line, match))
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
    return todos

def update_todo_file():
    """Update the TODO tracking file in Markdown format."""
    try:
        # Create backup of the TODO file if it exists
        if TODO_FILE.exists():
            shutil.copy(TODO_FILE, f"{TODO_FILE}.bak")
            
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            for todo_id, todo_info in sorted(tracked_todos.items()):
                file_path = todo_info['file']
                line_num = todo_info['line']
                content = todo_info['content']
                
                # Format ID with leading zeros (001, 002, etc.)
                formatted_id = f"{todo_id:03d}"
                
                # Create the markdown line in the requested format
                f.write(f"|| [{formatted_id}](./{file_path}#L{line_num}) | {content}\n")
        
        logging.info(f"Updated TODO file with {len(tracked_todos)} TODOs")
    except Exception as e:
        logging.error(f"Error updating TODO file: {e}")
        # Restore from backup if available
        if Path(f"{TODO_FILE}.bak").exists():
            shutil.copy(f"{TODO_FILE}.bak", TODO_FILE)

def update_todo_in_file(file_path, line_num, old_line, todo_id):
    """Update a TODO in a source file with its assigned ID."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        # Make sure line numbers match
        if line_num <= len(lines):
            pattern = get_todo_pattern(file_path)
            
            # Update the TODO format to include the ID
            # Only replace TODOx (without a number) with TODOx{todo_id}
            new_line = pattern.sub(
                lambda m: f"{m.group(1)}{m.group(2)}x{todo_id}{m.group(4)}{m.group(5)}{m.group(6)}", 
                old_line
            )
            
            # If the specialized pattern didn't work, try the default pattern
            if new_line == old_line and pattern != DEFAULT_TODO_PATTERN:
                new_line = DEFAULT_TODO_PATTERN.sub(
                    lambda m: f"{m.group(1)}{m.group(2)}x{todo_id}{m.group(4)}{m.group(5)}{m.group(6)}", 
                    old_line
                )
            
            # Only update if the line was actually changed
            if new_line != old_line:
                lines[line_num - 1] = new_line
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                logging.info(f"Updated TODO in {file_path} line {line_num} with ID {todo_id}")
                return True
    except Exception as e:
        logging.error(f"Error updating TODO in file {file_path}: {e}")
    return False

def remove_todo_from_file(file_path, line_num):
    """Remove a completed TODO from its source file."""
    try:
        # Ensure we have the full path to the file
        full_path = PROJECT_ROOT / file_path
        logging.info(f"Attempting to remove TODO from {full_path} at line {line_num}")
        
        if not full_path.exists():
            logging.error(f"File not found: {full_path}")
            return False
            
        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        if line_num <= len(lines):
            # Log the line before removal
            logging.info(f"Original line: {lines[line_num - 1].strip()}")
            
            # Remove the entire line containing the TODO
            lines[line_num - 1] = ""
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logging.info(f"Successfully removed completed TODO from {file_path} line {line_num}")
            return True
        else:
            logging.error(f"Line number {line_num} is out of range for file with {len(lines)} lines")
    except Exception as e:
        logging.error(f"Error removing TODO from file {file_path}: {e}")
    return False

def update_done_file(completed_todos_info):
    """Update the DONE file with completed TODOs and timestamps.
    
    Args:
        completed_todos_info: List of tuples (todo_id, file_path, line_num, content, timestamp)
    """
    try:
        # Append to the DONE file if it exists, otherwise create it
        with open(DONE_FILE, 'a', encoding='utf-8') as f:
            # Append new completed TODOs
            for todo_id, file_path, line_num, content, timestamp in completed_todos_info:
                # Format ID with leading zeros (001, 002, etc.)
                formatted_id = f"{todo_id:03d}"
                
                # Format as: timestamp ID <filepath#line> <comment>
                f.write(f"{timestamp} | [{formatted_id}]({file_path}#L{line_num}) | {content}\n")
        
        logging.info(f"Updated DONE file with {len(completed_todos_info)} completed TODOs")
    except Exception as e:
        logging.error(f"Error updating DONE file: {e}")

def check_completed_todos():
    """Check the TODO file for completed TODOs marked with |x|.
    Returns a tuple of (num_processed, num_failed)."""
    global tracked_todos
    completed_todos = []
    processed = 0
    failed = 0
    completed_todos_info = []  # Store info for DONE.md file
    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        if not TODO_FILE.exists():
            logging.warning("TODO file does not exist, skipping completed TODO check")
            return (0, 0)
            
        logging.info("Checking for completed TODOs...")
        
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for |x| pattern which indicates completed TODOs
        for line in content.splitlines():
            if line.startswith("|x|"):
                # Extract the TODO ID using regex for the new format with zero-padded IDs
                match = re.search(r'\|x\|\s*\[0*(\d+)\]', line)
                if match:
                    todo_id = int(match.group(1))
                    logging.info(f"Found completed TODO with ID {todo_id}: {line}")
                    completed_todos.append(todo_id)
    except Exception as e:
        logging.error(f"Error checking completed TODOs: {e}")
        return (0, 0)
        
    # Group completed TODOs by file to handle line number shifts properly
    todos_by_file = {}
    for todo_id in completed_todos:
        if todo_id in tracked_todos:
            todo_info = tracked_todos[todo_id]
            file_path = todo_info['file']
            if file_path not in todos_by_file:
                todos_by_file[file_path] = []
            todos_by_file[file_path].append((todo_id, todo_info))
            
            # Save info for DONE.md file
            completed_todos_info.append((
                todo_id, 
                file_path, 
                todo_info['line'], 
                todo_info['content'],
                current_timestamp
            ))
        else:
            logging.warning(f"Completed TODO {todo_id} not found in tracking")
            failed += 1
    
    # Process each file's TODOs in reverse line order (highest line number first)
    # This prevents line number shifts from affecting subsequent removals
    for file_path, todos in todos_by_file.items():
        # Sort by line number in reverse order
        todos.sort(key=lambda x: x[1]['line'], reverse=True)
        
        for todo_id, todo_info in todos:
            logging.info(f"Removing completed TODO {todo_id} from {file_path} line {todo_info['line']}")
            
            # Remove the TODO from its source file
            removed = remove_todo_from_file(file_path, todo_info['line'])
            if removed:
                # Remove from tracked TODOs
                del tracked_todos[todo_id]
                logging.info(f"Successfully removed completed TODO {todo_id} from tracking")
                processed += 1
            else:
                logging.error(f"Failed to remove completed TODO {todo_id} from file")
                failed += 1
    
    # Update the DONE file with completed TODOs
    if completed_todos_info:
        update_done_file(completed_todos_info)
    
    return (processed, failed)

def scan_for_todos():
    """Scan all files for TODOs and update tracking."""
    global tracked_todos, next_todo_id
    
    # Keep a copy of existing TODOs to avoid losing them
    previous_todos = tracked_todos.copy()
    
    # Reset tracking to rebuild it from scratch
    tracked_todos.clear()
    
    # Map of existing TODO IDs to maintain ID consistency
    existing_todo_ids = {}  # {(file_path, line_num): todo_id}
    
    # First, preserve IDs of existing TODOs (except completed ones)
    for todo_id, todo_info in previous_todos.items():
        existing_todo_ids[(todo_info['file'], todo_info['line'])] = todo_id
    
    # Find TODOs
    for file_path in find_files():
        try:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            str_path = str(rel_path)
            
            todos = extract_todos_from_file(file_path)
            for line_num, line_content, match in todos:
                prefix, todo_keyword, existing_id, colon_space, todo_text, end = match.groups()
                
                # Check if this TODO already has an ID
                if existing_id:
                    todo_id = int(existing_id)
                    # Update next_todo_id if necessary
                    next_todo_id = max(next_todo_id, todo_id + 1)
                else:
                    # Check if this line already has a tracked TODO
                    if (str_path, line_num) in existing_todo_ids:
                        todo_id = existing_todo_ids[(str_path, line_num)]
                    else:
                        # Assign new ID
                        todo_id = next_todo_id
                        next_todo_id += 1
                        # Update source file
                        update_todo_in_file(file_path, line_num, line_content, todo_id)
                
                # Add to tracking
                tracked_todos[todo_id] = {
                    'file': str_path,
                    'line': line_num,
                    'content': todo_text.strip()
                }
                existing_todo_ids[(str_path, line_num)] = todo_id
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
    
    # Check for TODOs that were in previous scan but not in this scan (deleted TODOs)
    deleted_todos_info = []
    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    for todo_id, todo_info in previous_todos.items():
        if todo_id not in tracked_todos:
            # This TODO was in the previous scan but not in the current scan, likely deleted
            logging.info(f"Detected deleted TODO {todo_id} from {todo_info['file']} line {todo_info['line']}")
            
            # Add to the list of deleted TODOs to be added to DONE.md
            deleted_todos_info.append((
                todo_id,
                todo_info['file'],
                todo_info['line'],
                todo_info['content'],
                current_timestamp
            ))
    
    # Update the DONE file with deleted TODOs
    if deleted_todos_info:
        update_done_file(deleted_todos_info)
        logging.info(f"Marked {len(deleted_todos_info)} deleted TODOs as completed")
    
    # NOW check for completed TODOs AFTER the tracking dictionary has been built
    processed, failed = check_completed_todos()
    
    # Update the TODO file AFTER completed TODOs have been processed
    update_todo_file()
    
    # Return combined results of manual completions and auto-detected deletions
    return processed + len(deleted_todos_info), failed

def test_remove_todo():
    """Test function to manually remove a completed TODO."""
    global tracked_todos
    
    # Read the TODO file
    if not TODO_FILE.exists():
        logging.error("TODO file does not exist")
        return
        
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find lines with |x|
    completed_lines = [line for line in content.splitlines() if line.startswith("|x|")]
    
    if not completed_lines:
        logging.error("No completed TODOs found in the TODO file")
        return
        
    for line in completed_lines:
        logging.info(f"Processing completed TODO line: {line}")
        
        # Extract information from the new markdown format with zero-padded IDs
        match = re.search(r'\|x\|\s*\[0*(\d+)\]\((\.\/)(.*?)#L(\d+)\)\s*\|\s*(.*)', line)
        if match:
            todo_id = int(match.group(1))
            file_path = match.group(3)
            line_num = int(match.group(4))
            todo_content = match.group(5).strip()
            
            logging.info(f"Test removing TODO {todo_id} from {file_path} line {line_num}")
            
            # Ensure the TODO is in our tracking
            if todo_id not in tracked_todos:
                tracked_todos[todo_id] = {
                    'file': file_path, 
                    'line': line_num,
                    'content': todo_content
                }
            
            # Remove the TODO
            try:
                full_path = PROJECT_ROOT / file_path
                if not full_path.exists():
                    logging.error(f"File not found: {full_path}")
                    continue
                    
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    
                if line_num <= len(lines):
                    logging.info(f"Original line: {lines[line_num - 1].strip()}")
                    lines[line_num - 1] = ""  # Remove the TODO line
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                        
                    logging.info(f"Removed TODO {todo_id} from {file_path}")
                    
                    # Remove from tracked TODOs
                    if todo_id in tracked_todos:
                        del tracked_todos[todo_id]
                    
                    # Update the TODO.md file with remaining TODOs
                    update_todo_file()
                        
                    logging.info(f"Updated TODO file, removed TODO {todo_id}")
                else:
                    logging.error(f"Line number {line_num} is out of range for file with {len(lines)} lines")
            except Exception as e:
                logging.error(f"Error removing TODO {todo_id}: {e}")
        else:
            logging.error(f"Could not parse completed TODO line: {line}")

def main():
    """Main entry point for the TODO scanner. First builds tracking dictionary,
    then checks for completed TODOs, and finally updates the TODO file.
    """
    # Set up logging
    initialize_logging()
    
    # Set up config 
    load_config()
    
    # Initial scan to build tracking dictionary, check completed TODOs, and update the TODO file
    logging.info("Initial scan for TODOs...")
    processed, failed = scan_for_todos()
    logging.info(f"Initial scan complete. Processed {processed} completed TODOs and had {failed} failures. Found {len(tracked_todos)} active TODOs.")
    
    # Log initial DONE file status
    if DONE_FILE.exists():
        with open(DONE_FILE, 'r', encoding='utf-8') as f:
            done_count = len(f.readlines())
        logging.info(f"DONE file contains {done_count} completed TODOs")
    else:
        logging.info("DONE file does not exist yet. It will be created when TODOs are completed.")
    
    # Run the main loop
    while True:
        try:
            logging.info("Scanning for TODOs...")
            processed, failed = scan_for_todos()
            logging.info(f"Scan complete. Processed {processed} completed TODOs and had {failed} failures. Found {len(tracked_todos)} active TODOs. Next scan in {CHECK_INTERVAL/60} minutes.")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Exiting...")
            break
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            logging.info(f"Retrying in {CHECK_INTERVAL/60} minutes...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 