"""
Django management command to restore missing COM ID entries from comlist Excel files.

This command reads the comlist Excel files for projects and updates the Document models
with the COM IDs that may have been missed during initial processing.

Usage:
    python manage.py restore_com_ids                    # Process all projects
    python manage.py restore_com_ids --project-id 123   # Process specific project
    python manage.py restore_com_ids --dry-run          # Show what would be updated without saving
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from microapp.models import Project, Document
import openpyxl
import xlrd
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Restore missing COM ID entries from comlist Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Process only the specified project ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually saving changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update COM IDs even if they already exist (overwrite)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each document processed',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        self.verbose = options['verbose']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be saved to database')
            )
        
        # Get projects to process
        if options['project_id']:
            try:
                projects = [Project.objects.get(id=options['project_id'])]
            except Project.DoesNotExist:
                raise CommandError(f'Project with ID {options["project_id"]} does not exist')
        else:
            projects = Project.objects.filter(comlist_path__isnull=False).exclude(comlist_path='')
        
        if not projects:
            self.stdout.write(
                self.style.WARNING('No projects found with comlist_path set')
            )
            return
        
        self.stdout.write(f'Processing {len(projects)} project(s)...\n')
        
        total_updated = 0
        total_errors = 0
        
        for project in projects:
            try:
                updated_count = self.process_project(project)
                total_updated += updated_count
                
                if updated_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Project {project.archive_id}: Updated {updated_count} COM IDs'
                        )
                    )
                else:
                    self.stdout.write(
                        f'  Project {project.archive_id}: No updates needed'
                    )
                    
            except Exception as e:
                total_errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Project {project.archive_id}: Error - {str(e)}'
                    )
                )
                if self.verbose:
                    import traceback
                    self.stdout.write(traceback.format_exc())
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'SUMMARY:')
        self.stdout.write(f'  Total COM IDs updated: {total_updated}')
        self.stdout.write(f'  Projects with errors: {total_errors}')
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('  (DRY RUN - No actual changes made)')
            )

    def process_project(self, project):
        """Process a single project to restore COM IDs."""
        
        if self.verbose:
            self.stdout.write(f'\nProcessing project: {project.archive_id}')
            self.stdout.write(f'  Comlist path: {project.comlist_path}')
        
        # Check if comlist file exists
        if not project.comlist_path or not os.path.exists(project.comlist_path):
            if self.verbose:
                self.stdout.write(f'  Skipping - comlist file not found')
            return 0
        
        # Read COM ID mappings from Excel file
        com_id_mappings = self.read_com_id_mappings(project.comlist_path)
        
        if not com_id_mappings:
            if self.verbose:
                self.stdout.write(f'  No COM ID mappings found in Excel file')
            return 0
        
        if self.verbose:
            self.stdout.write(f'  Found {len(com_id_mappings)} COM ID mappings in Excel')
        
        # Get documents for this project
        documents = Document.objects.filter(project=project)
        
        if not documents.exists():
            if self.verbose:
                self.stdout.write(f'  No documents found for this project')
            return 0
        
        updated_count = 0
        
        # Process each document
        for document in documents:
            try:
                # Check if we should update this document
                if not self.force and document.com_id is not None:
                    if self.verbose:
                        self.stdout.write(f'    {document.doc_id}: Already has COM ID {document.com_id} (use --force to overwrite)')
                    continue
                
                # Try to find COM ID for this document
                doc_id_base = document.doc_id.replace('.pdf', '') if document.doc_id.endswith('.pdf') else document.doc_id
                
                # Look up COM ID in mappings
                com_id = com_id_mappings.get(doc_id_base)
                
                # If not found, try normalized version
                if com_id is None:
                    try:
                        normalized_id = str(int(float(doc_id_base)))
                        com_id = com_id_mappings.get(normalized_id)
                    except (ValueError, TypeError):
                        pass
                
                if com_id is not None:
                    old_com_id = document.com_id
                    
                    if not self.dry_run:
                        document.com_id = com_id
                        document.save()
                    
                    updated_count += 1
                    
                    if self.verbose:
                        if old_com_id is not None:
                            self.stdout.write(f'    {document.doc_id}: Updated COM ID {old_com_id} → {com_id}')
                        else:
                            self.stdout.write(f'    {document.doc_id}: Set COM ID to {com_id}')
                else:
                    if self.verbose:
                        self.stdout.write(f'    {document.doc_id}: No COM ID found in mappings')
                        
            except Exception as e:
                if self.verbose:
                    self.stdout.write(f'    {document.doc_id}: Error - {str(e)}')
                continue
        
        return updated_count

    def read_com_id_mappings(self, comlist_path):
        """Read COM ID mappings from Excel file (.xls or .xlsx)."""
        
        com_id_mappings = {}
        file_extension = Path(comlist_path).suffix.lower()
        
        try:
            if self.verbose:
                self.stdout.write(f'  Opening Excel file: {comlist_path} (format: {file_extension})')
            
            if file_extension == '.xls':
                # Use xlrd for .xls files
                data = self._read_xls_file(comlist_path)
            elif file_extension == '.xlsx':
                # Use openpyxl for .xlsx files
                data = self._read_xlsx_file(comlist_path)
            else:
                raise Exception(f'Unsupported file format: {file_extension}')
            
            if not data:
                return com_id_mappings
            
            # Skip header row if exists
            start_row = 1 if data and isinstance(data[0][0], str) and not str(data[0][0]).isdigit() else 0
            
            if self.verbose:
                self.stdout.write(f'  Processing {len(data)} rows, starting at row {start_row}')
            
            # Extract barcode and ComID pairs
            for i in range(start_row, len(data)):
                if i < len(data) and len(data[i]) >= 2:
                    barcode_raw = data[i][0]
                    com_id = data[i][1]
                    
                    # Skip empty rows
                    if barcode_raw is None and com_id is None:
                        continue
                    
                    # Process barcode formats
                    barcode_original = str(barcode_raw) if barcode_raw is not None else None
                    
                    # Create normalized version
                    try:
                        if isinstance(barcode_raw, float) and barcode_raw.is_integer():
                            barcode_normalized = str(int(barcode_raw))
                        elif isinstance(barcode_raw, int):
                            barcode_normalized = str(barcode_raw)
                        else:
                            barcode_normalized = str(int(float(str(barcode_raw))))
                    except (ValueError, TypeError, AttributeError):
                        barcode_normalized = barcode_original
                    
                    # Process COM ID
                    if com_id is not None:
                        try:
                            if isinstance(com_id, float) and com_id.is_integer():
                                com_id = int(com_id)
                            else:
                                com_id = int(com_id)
                            
                            # Store both formats in mappings
                            if barcode_original and com_id:
                                com_id_mappings[barcode_original] = com_id
                            if barcode_normalized and com_id:
                                com_id_mappings[barcode_normalized] = com_id
                                
                        except (ValueError, TypeError):
                            continue
            
            if self.verbose:
                self.stdout.write(f'  Extracted {len(com_id_mappings)} COM ID mappings')
            
        except Exception as e:
            raise Exception(f'Error reading Excel file: {str(e)}')
        
        return com_id_mappings
    
    def _read_xlsx_file(self, file_path):
        """Read .xlsx file using openpyxl."""
        wb = None
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            data = list(ws.values)
            return data
        finally:
            if wb:
                try:
                    wb.close()
                except Exception:
                    pass
    
    def _read_xls_file(self, file_path):
        """Read .xls file using xlrd."""
        wb = None
        try:
            wb = xlrd.open_workbook(file_path)
            ws = wb.sheet_by_index(0)
            
            # Convert xlrd data to list format similar to openpyxl
            data = []
            for row_idx in range(ws.nrows):
                row_data = []
                for col_idx in range(ws.ncols):
                    cell_value = ws.cell_value(row_idx, col_idx)
                    # Convert xlrd cell types to Python types
                    if ws.cell_type(row_idx, col_idx) == xlrd.XL_CELL_EMPTY:
                        cell_value = None
                    elif ws.cell_type(row_idx, col_idx) == xlrd.XL_CELL_NUMBER:
                        # Check if it's actually an integer
                        if cell_value == int(cell_value):
                            cell_value = int(cell_value)
                    row_data.append(cell_value)
                data.append(row_data)
            
            return data
        finally:
            # xlrd doesn't need explicit closing
            pass 