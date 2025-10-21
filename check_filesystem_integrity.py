#!/usr/bin/env python3
"""
Script to check filesystem integrity against database records.
Validates projects, rolls, and documents to find mismatches and orphaned files.
"""

import os
import sys
import django
from pathlib import Path
from collections import defaultdict
import json

# Add the project directory to Python path
project_dir = os.path.join(os.path.dirname(__file__), 'micro')
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'micro.settings')
django.setup()

from microapp.models import Project, Roll, Document, ProcessedDocument

class FilesystemIntegrityChecker:
    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = {
            'projects_checked': 0,
            'rolls_checked': 0,
            'documents_checked': 0,
            'orphaned_directories': 0,
            'missing_directories': 0,
            'document_mismatches': 0,
            'valid_projects': 0
        }
    
    def check_all_projects(self):
        """Check all projects for filesystem integrity."""
        print("🔍 Starting filesystem integrity check...")
        print("=" * 80)
        
        projects = Project.objects.all().order_by('id')
        
        for project in projects:
            self.check_project_integrity(project)
        
        self.print_summary()
        self.print_detailed_issues()
    
    def check_project_integrity(self, project):
        """Check a single project's integrity."""
        self.stats['projects_checked'] += 1
        project_issues = []
        
        print(f"\n📁 Checking Project {project.id}: {project.archive_id} ({project.location})")
        
        # Check project directory
        if project.project_path:
            try:
                # Handle Unicode characters in paths
                project_path = Path(project.project_path).resolve()
                if not project_path.exists():
                    issue = f"Project directory missing: {project.project_path}"
                    project_issues.append(issue)
                    print(f"  ❌ {issue}")
                    self.stats['missing_directories'] += 1
                else:
                    print(f"  ✅ Project directory exists: {project.project_path}")
            except (OSError, UnicodeError) as e:
                issue = f"Error accessing project directory: {project.project_path} - {e}"
                project_issues.append(issue)
                print(f"  ❌ {issue}")
        
        # Check output directory
        if project.output_dir:
            try:
                output_path = Path(project.output_dir).resolve()
                if not output_path.exists():
                    issue = f"Output directory missing: {project.output_dir}"
                    project_issues.append(issue)
                    print(f"  ❌ {issue}")
                    self.stats['missing_directories'] += 1
                else:
                    print(f"  ✅ Output directory exists: {project.output_dir}")
                    # Look for .output subdirectory
                    dot_output_path = output_path / '.output'
                    if dot_output_path.exists():
                        print(f"    📁 Found .output subdirectory")
                        self.check_rolls_in_output_directory(project, dot_output_path, project_issues)
                    else:
                        # Check if the output_path itself contains roll directories
                        print(f"    📁 No .output subdirectory, checking main directory for rolls")
                        self.check_rolls_in_output_directory(project, output_path, project_issues)
            except (OSError, UnicodeError) as e:
                issue = f"Error accessing output directory: {project.output_dir} - {e}"
                project_issues.append(issue)
                print(f"  ❌ {issue}")
        
        # Check rolls and their documents
        rolls = project.rolls.all()
        print(f"  📼 Checking {rolls.count()} rolls...")
        
        for roll in rolls:
            self.check_roll_integrity(project, roll, project_issues)
        
        if not project_issues:
            self.stats['valid_projects'] += 1
            print(f"  ✅ Project {project.id} is valid")
        else:
            self.issues[f"Project {project.id} ({project.archive_id})"] = project_issues
    
    def check_rolls_in_output_directory(self, project, output_path, project_issues):
        """Check rolls in the output directory against database."""
        if not output_path.exists():
            return
        
        # This function now handles both .output directories and main project directories
        
        # Get roll directories from filesystem (only 8-digit film numbers)
        fs_roll_dirs = set()
        all_dirs = []
        for item in output_path.iterdir():
            if item.is_dir():
                all_dirs.append(item.name)
                if self.looks_like_roll_directory(item):
                    fs_roll_dirs.add(item.name)
        
        print(f"      📁 Found {len(all_dirs)} directories: {all_dirs[:5]}{'...' if len(all_dirs) > 5 else ''}")
        print(f"      🎬 Roll directories (8-digit, starts with 1/2): {sorted(fs_roll_dirs)}")
        
        # Get roll directories from database
        db_rolls = set()
        print(f"      🗄️  Database rolls for project:")
        for roll in project.rolls.all():
            print(f"         Roll {roll.id}: film_number={roll.film_number}, output_dir={roll.output_directory}")
            
            if roll.output_directory:
                roll_dir_name = Path(roll.output_directory).name
                db_rolls.add(roll_dir_name)
            elif roll.film_number:
                # Film number should match directory name exactly
                if roll.film_number in fs_roll_dirs:
                    db_rolls.add(roll.film_number)
        
        print(f"      🗄️  Expected roll directories: {sorted(db_rolls)}")
        
        # Find orphaned directories (in filesystem but not in database)
        orphaned = fs_roll_dirs - db_rolls
        if orphaned:
            for orphan in orphaned:
                issue = f"Orphaned roll directory: {output_path / orphan}"
                project_issues.append(issue)
                print(f"    ❌ {issue}")
                self.stats['orphaned_directories'] += 1
        
        # Find missing directories (in database but not in filesystem)
        missing = db_rolls - fs_roll_dirs
        if missing:
            for missing_dir in missing:
                # Double-check if the directory actually exists with a different case or pattern
                missing_path = output_path / missing_dir
                if not missing_path.exists():
                    # Try to find a similar directory (case insensitive)
                    found_similar = False
                    try:
                        for item in output_path.iterdir():
                            if item.is_dir() and item.name.lower() == missing_dir.lower():
                                found_similar = True
                                print(f"    ⚠️  Directory exists with different case: {item.name} (expected: {missing_dir})")
                                break
                    except PermissionError:
                        pass
                    
                    if not found_similar:
                        issue = f"Missing roll directory: {missing_path}"
                        project_issues.append(issue)
                        print(f"    ❌ {issue}")
                        self.stats['missing_directories'] += 1
                else:
                    print(f"    ✅ Directory exists: {missing_path}")
    
    def check_roll_integrity(self, project, roll, project_issues):
        """Check a single roll's integrity."""
        self.stats['rolls_checked'] += 1
        
        print(f"    📼 Roll {roll.roll_id}: {roll.film_number}")
        
        # Check roll output directory
        if roll.output_directory:
            roll_path = Path(roll.output_directory)
            if not roll_path.exists():
                issue = f"Roll directory missing: {roll.output_directory}"
                project_issues.append(issue)
                print(f"      ❌ {issue}")
                self.stats['missing_directories'] += 1
                return
            else:
                print(f"      ✅ Roll directory exists: {roll.output_directory}")
                # Check documents in roll directory
                self.check_documents_in_roll_directory(project, roll, roll_path, project_issues)
        else:
            print(f"      ⚠️  No output directory set for roll {roll.roll_id}")
    
    def check_documents_in_roll_directory(self, project, roll, roll_path, project_issues):
        """Check documents in roll directory against database."""
        if not roll_path.exists():
            return
        
        # Get PDF files from filesystem (case insensitive)
        fs_documents = set()
        pdf_files = []
        
        # Check for both .pdf and .PDF files
        pdf_files.extend(list(roll_path.glob("*.pdf")))
        pdf_files.extend(list(roll_path.glob("*.PDF")))
        
        for pdf_file in pdf_files:
            # Handle double extensions like .pdf.pdf
            doc_name = pdf_file.name
            if doc_name.lower().endswith('.pdf.pdf'):
                # Remove both .pdf extensions
                doc_name = doc_name[:-8]  # Remove .pdf.pdf
            elif doc_name.lower().endswith('.pdf'):
                # Remove single .pdf extension
                doc_name = doc_name[:-4]  # Remove .pdf
            
            fs_documents.add(doc_name)
        
        # Get documents from database (via ProcessedDocument or DocumentSegment)
        db_documents = set()
        
        # Check ProcessedDocument entries for this roll
        processed_docs = ProcessedDocument.objects.filter(roll=roll)
        for proc_doc in processed_docs:
            if proc_doc.output_path:
                output_file = Path(proc_doc.output_path)
                if output_file.suffix.lower() == '.pdf':
                    # Handle double extensions
                    filename = output_file.name
                    if filename.lower().endswith('.pdf.pdf'):
                        doc_name = filename[:-8]  # Remove .pdf.pdf
                    elif filename.lower().endswith('.pdf'):
                        doc_name = filename[:-4]  # Remove .pdf
                    else:
                        doc_name = output_file.stem
                    db_documents.add(doc_name)
        
        # Also check DocumentSegments for this roll
        segments = roll.document_segments.all()
        for segment in segments:
            # Try to find the expected filename pattern
            doc_id = segment.document.doc_id
            db_documents.add(doc_id)
        
        # If no processed documents found, try to get documents from the project
        if not db_documents and not processed_docs.exists():
            # Get all documents for this project and assume they might be in this roll
            project_docs = project.documents.all()
            for doc in project_docs:
                db_documents.add(doc.doc_id)
        
        print(f"        📄 Found {len(fs_documents)} PDF files, expected {len(db_documents)} documents")
        
        # Debug output for troubleshooting
        if len(sys.argv) > 1 and sys.argv[1] == "debug":
            print(f"        🔍 Debug - Filesystem documents: {sorted(fs_documents)}")
            print(f"        🔍 Debug - Database documents: {sorted(db_documents)}")
        
        # Check for exact match
        if fs_documents == db_documents:
            print(f"        ✅ Document count matches exactly")
        else:
            # Before reporting mismatches, try some fuzzy matching
            # Check if filesystem documents are substrings or contain database documents
            matched_docs = set()
            for db_doc in db_documents:
                for fs_doc in fs_documents:
                    # Check if they match (case insensitive or partial match)
                    if (db_doc.lower() == fs_doc.lower() or 
                        db_doc in fs_doc or 
                        fs_doc in db_doc or
                        # Check if one is a numeric prefix of the other (common pattern)
                        (db_doc.isdigit() and fs_doc.startswith(db_doc)) or
                        (fs_doc.isdigit() and db_doc.startswith(fs_doc))):
                        matched_docs.add(db_doc)
                        break
            
            # Recalculate actual mismatches after fuzzy matching
            unmatched_db = db_documents - matched_docs
            unmatched_fs = set()
            for fs_doc in fs_documents:
                found_match = False
                for db_doc in db_documents:
                    if (db_doc.lower() == fs_doc.lower() or 
                        db_doc in fs_doc or 
                        fs_doc in db_doc or
                        (db_doc.isdigit() and fs_doc.startswith(db_doc)) or
                        (fs_doc.isdigit() and db_doc.startswith(fs_doc))):
                        found_match = True
                        break
                if not found_match:
                    unmatched_fs.add(fs_doc)
            
            if not unmatched_db and not unmatched_fs:
                print(f"        ✅ Documents match (with fuzzy matching)")
            else:
                self.stats['document_mismatches'] += 1
                
                # Find orphaned files (in filesystem but not in database)
                if unmatched_fs:
                    for orphan in sorted(unmatched_fs):
                        issue = f"Orphaned document file: {roll_path / (orphan + '.pdf')}"
                        project_issues.append(issue)
                        print(f"        ❌ {issue}")
                
                # Find missing files (in database but not in filesystem)
                if unmatched_db:
                    for missing in sorted(unmatched_db):
                        issue = f"Missing document file: {roll_path / (missing + '.pdf')}"
                        project_issues.append(issue)
                        print(f"        ❌ {issue}")
        
        # Update document count
        self.stats['documents_checked'] += len(fs_documents)
    
    def find_orphaned_output_directories(self):
        """Find output directories that don't belong to any project."""
        print("\n🗂️  Checking for orphaned output directories...")
        
        # Common output directory patterns to check
        common_paths = [
            Path("X:/"),  # Common project drive
            Path("Y:/"),  # Alternative drive
            Path("Z:/"),  # Another alternative
        ]
        
        # Get all project output directories from database
        db_output_dirs = set()
        for project in Project.objects.all():
            if project.output_dir:
                db_output_dirs.add(Path(project.output_dir).resolve())
            if project.project_path:
                db_output_dirs.add(Path(project.project_path).resolve())
        
        orphaned_dirs = []
        
        for base_path in common_paths:
            if not base_path.exists():
                continue
            
            try:
                # Look for directories that match project patterns
                for item in base_path.iterdir():
                    if item.is_dir():
                        # Check if this looks like a project directory
                        if self.looks_like_project_directory(item):
                            item_resolved = item.resolve()
                            if item_resolved not in db_output_dirs:
                                orphaned_dirs.append(item)
            except PermissionError:
                print(f"      ⚠️  Permission denied accessing {base_path}")
                continue
        
        if orphaned_dirs:
            print(f"      ❌ Found {len(orphaned_dirs)} potentially orphaned directories:")
            for orphan_dir in sorted(orphaned_dirs):
                print(f"        - {orphan_dir}")
                self.issues["Orphaned Directories"].append(str(orphan_dir))
        else:
            print(f"      ✅ No orphaned directories found")
    
    def looks_like_roll_directory(self, directory):
        """Check if a directory looks like a roll directory (film number format)."""
        dir_name = directory.name
        
        # Roll directories are 8-digit numbers starting with 1 or 2
        if (dir_name.isdigit() and 
            len(dir_name) == 8 and 
            dir_name.startswith(('1', '2'))):
            return True
        
        return False
    
    def looks_like_project_directory(self, directory):
        """Check if a directory looks like a project directory."""
        dir_name = directory.name
        
        # Check for common project patterns
        patterns = [
            "RRD",  # Archive ID pattern
            "_OU_", "_DW_",  # Location patterns
        ]
        
        for pattern in patterns:
            if pattern in dir_name:
                return True
        
        # Check if it contains roll subdirectories
        try:
            for item in directory.iterdir():
                if item.is_dir() and self.looks_like_roll_directory(item):
                    return True
        except PermissionError:
            pass
        
        return False
    
    def print_summary(self):
        """Print summary statistics."""
        print("\n" + "=" * 80)
        print("📊 INTEGRITY CHECK SUMMARY")
        print("=" * 80)
        print(f"Projects checked: {self.stats['projects_checked']}")
        print(f"Rolls checked: {self.stats['rolls_checked']}")
        print(f"Documents checked: {self.stats['documents_checked']}")
        print(f"Valid projects: {self.stats['valid_projects']}")
        print(f"Projects with issues: {len(self.issues)}")
        print(f"Orphaned directories: {self.stats['orphaned_directories']}")
        print(f"Missing directories: {self.stats['missing_directories']}")
        print(f"Document mismatches: {self.stats['document_mismatches']}")
    
    def print_detailed_issues(self):
        """Print detailed issues found."""
        if not self.issues:
            print("\n✅ No issues found! All projects are in sync with filesystem.")
            return
        
        print("\n" + "=" * 80)
        print("🚨 DETAILED ISSUES")
        print("=" * 80)
        
        for entity, issue_list in self.issues.items():
            print(f"\n❌ {entity}:")
            for issue in issue_list:
                print(f"   - {issue}")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Review orphaned directories - they may be safe to delete")
        print("2. Check missing directories - projects may need to be re-processed")
        print("3. Investigate document mismatches - files may have been moved or deleted")
        print("4. Consider running cleanup scripts for orphaned directories")
    
    def export_issues_to_json(self, filename="filesystem_issues.json"):
        """Export issues to JSON file for further processing."""
        export_data = {
            'timestamp': str(django.utils.timezone.now()),
            'stats': self.stats,
            'issues': dict(self.issues)
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\n📄 Issues exported to: {filename}")

def main():
    """Main function to run the integrity check."""
    checker = FilesystemIntegrityChecker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "debug":
            # Run full check with debug output
            checker.check_all_projects()
            checker.find_orphaned_output_directories()
        elif sys.argv[1] == "project":
            # Check specific project
            if len(sys.argv) > 2:
                try:
                    project_id = int(sys.argv[2])
                    project = Project.objects.get(id=project_id)
                    checker.check_project_integrity(project)
                except (ValueError, Project.DoesNotExist):
                    print(f"❌ Invalid project ID: {sys.argv[2]}")
            else:
                print("❌ Please provide a project ID")
                print("Usage: python check_filesystem_integrity.py project <project_id>")
        elif sys.argv[1] == "orphans":
            # Check for orphaned directories only
            checker.find_orphaned_output_directories()
        elif sys.argv[1] == "export":
            # Run full check and export results
            checker.check_all_projects()
            checker.find_orphaned_output_directories()
            filename = sys.argv[2] if len(sys.argv) > 2 else "filesystem_issues.json"
            checker.export_issues_to_json(filename)
        else:
            print("❌ Unknown command")
            print("Usage:")
            print("  python check_filesystem_integrity.py                    # Full check")
            print("  python check_filesystem_integrity.py debug              # Full check with debug output")
            print("  python check_filesystem_integrity.py project <id>       # Check specific project")
            print("  python check_filesystem_integrity.py orphans            # Find orphaned directories")
            print("  python check_filesystem_integrity.py export [filename]  # Export results to JSON")
    else:
        # Run full check
        checker.check_all_projects()
        checker.find_orphaned_output_directories()

if __name__ == "__main__":
    main()
