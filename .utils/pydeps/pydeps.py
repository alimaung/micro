import os
import ast
import sys
import json
from pathlib import Path
from collections import defaultdict

def get_standard_library_modules():
    """Get a set of Python standard library module names."""
    stdlib_modules = set(sys.stdlib_module_names)
    # Add some common built-in modules that might not be in stdlib_module_names
    stdlib_modules.update(['builtins', '__builtin__', '__future__'])
    return stdlib_modules

def extract_imports_from_file(file_path):
    """Extract all import statements from a Python file."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        # Skip files that can't be parsed or read
        pass
    
    return imports

def scan_python_files(directory):
    """Scan all .py files in the given directory recursively, grouped by first, second and third level directories."""
    dependencies_by_dir = defaultdict(set)
    stdlib_modules = get_standard_library_modules()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_imports = extract_imports_from_file(file_path)
                # Exclude standard library modules
                external_imports = file_imports - stdlib_modules
                
                # Get the directory path relative to the base directory
                rel_path = os.path.relpath(root, directory)
                if rel_path == '.':
                    dir_key = 'root'
                else:
                    path_parts = rel_path.split(os.sep)
                    # Take up to 3 levels of directory depth
                    dir_key = '/'.join(path_parts[:3])
                
                dependencies_by_dir[dir_key].update(external_imports)
    
    # Convert sets to sorted lists and create nested structure
    result = {}
    for dir_path, deps in dependencies_by_dir.items():
        if deps:  # Only include directories with dependencies
            result[dir_path] = sorted(deps)
    
    return result

def main():
    """Main function to scan Y:\\micro\\ and save results."""
    directory = r"Y:\micro"
    json_output_file = "dependencies.json"
    requirements_output_file = "requirements.txt"
    
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist!")
        return
    
    print(f"Scanning Python files in {directory}...")
    dependencies_by_dir = scan_python_files(directory)
    
    # Save results to JSON file
    with open(json_output_file, 'w', encoding='utf-8') as f:
        json.dump(dependencies_by_dir, f, indent=2, ensure_ascii=False)
    
    # Collect all unique dependencies for requirements.txt
    all_deps = set()
    for deps in dependencies_by_dir.values():
        all_deps.update(deps)
    
    # Save requirements.txt
    with open(requirements_output_file, 'w', encoding='utf-8') as f:
        for dep in sorted(all_deps):
            f.write(f"{dep}\n")
    
    print(f"Found dependencies in {len(dependencies_by_dir)} directory paths")
    print(f"Total unique dependencies: {len(all_deps)}")
    print(f"Results saved to {json_output_file}")
    print(f"Requirements saved to {requirements_output_file}")

if __name__ == "__main__":
    main()
