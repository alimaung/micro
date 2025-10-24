"""
Django management command to restore missing COM ID entries from comlist Excel files.

This command reads the comlist Excel files for projects and updates the Document models
with the COM IDs that may have been missed during initial processing.

Usage:
    python manage.py restore_com_ids                    # Process all projects with comlist_path
    python manage.py restore_com_ids --batch           # Process only projects with missing COM IDs
    python manage.py restore_com_ids --project-id 123   # Process specific project
    python manage.py restore_com_ids --dry-run          # Show what would be updated without saving
    python manage.py restore_com_ids --exclude-xrrd     # Exclude projects with XRRD in archive_id
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from microapp.models import Project, Document
import openpyxl
import xlrd
import os
import re
from pathlib import Path


def validate_barcode(barcode: str) -> tuple[bool, str]:
    """
    Validate that barcode is exactly 16 digits.
    
    Args:
        barcode: Barcode string to validate
        
    Returns:
        Tuple of (is_valid, normalized_barcode)
    """
    if not barcode:
        return False, ""
    
    # Remove any whitespace and convert to string
    clean_barcode = str(barcode).strip()
    
    # Check if it's exactly 16 digits
    if re.match(r'^\d{16}$', clean_barcode):
        return True, clean_barcode
    
    # Try to extract 16 consecutive digits
    digits_only = re.sub(r'\D', '', clean_barcode)
    if len(digits_only) == 16:
        return True, digits_only
    
    return False, clean_barcode

def validate_com_id(com_id) -> tuple[bool, str]:
    """
    Validate that COM ID is exactly 8 digits.
    
    Args:
        com_id: COM ID to validate (can be string, int, float)
        
    Returns:
        Tuple of (is_valid, normalized_com_id)
    """
    if com_id is None:
        return False, ""
    
    # Handle different input types
    if isinstance(com_id, (int, float)):
        # Convert to integer if it's a whole number
        if isinstance(com_id, float) and com_id.is_integer():
            com_id = int(com_id)
        clean_com_id = str(com_id)
    else:
        clean_com_id = str(com_id).strip()
    
    # Remove any non-digit characters
    digits_only = re.sub(r'\D', '', clean_com_id)
    
    # Check if it's exactly 8 digits
    if len(digits_only) == 8:
        return True, digits_only
    
    # Check if it's less than 8 digits and pad with leading zeros
    if len(digits_only) <= 8 and len(digits_only) > 0:
        padded_com_id = digits_only.zfill(8)
        return True, padded_com_id
    
    return False, clean_com_id

def normalize_document_id(doc_id: str) -> str:
    """
    Normalize document ID by removing .pdf extension and ensuring proper format.
    
    Args:
        doc_id: Document ID to normalize
        
    Returns:
        Normalized document ID
    """
    if not doc_id:
        return ""
    
    # Convert to string and strip whitespace
    normalized = str(doc_id).strip()
    
    # Remove .pdf extension (case-insensitive)
    if normalized.lower().endswith('.pdf'):
        normalized = normalized[:-4]
    
    return normalized

class Command(BaseCommand):
    help = 'Restore missing COM ID entries from comlist Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Process only the specified project ID',
        )
        parser.add_argument(
            '--batch',
            action='store_true',
            help='Process all projects with missing COM IDs (requires comlist_path)',
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
        parser.add_argument(
            '--exclude-xrrd',
            action='store_true',
            help='Exclude projects with XRRD in their archive_id',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        self.verbose = options['verbose']
        self.batch = options['batch']
        self.exclude_xrrd = options['exclude_xrrd']
        
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
        elif self.batch:
            # Get projects with missing COM IDs that have comlist_path
            projects = self.get_projects_with_missing_com_ids()
        else:
            projects = Project.objects.filter(comlist_path__isnull=False).exclude(comlist_path='')
        
        # Apply XRRD exclusion filter if requested
        if self.exclude_xrrd:
            projects = [p for p in projects if 'XRRD' not in p.archive_id]
            if self.verbose:
                self.stdout.write('Excluding projects with XRRD in archive_id')
        
        if not projects:
            if self.batch:
                self.stdout.write(
                    self.style.SUCCESS('No projects found with missing COM IDs and comlist_path')
                )
            else:
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

    def get_projects_with_missing_com_ids(self):
        """Get projects that have documents with missing COM IDs and have comlist_path set."""
        from django.db.models import Q
        
        # Get all projects with comlist_path
        projects_with_comlist = Project.objects.filter(
            comlist_path__isnull=False
        ).exclude(comlist_path='')
        
        projects_with_missing_com_ids = []
        
        for project in projects_with_comlist:
            # Skip XRRD projects if exclusion is enabled
            if self.exclude_xrrd and 'XRRD' in project.archive_id:
                continue
                
            # Check if this project has documents without COM IDs
            documents_without_com_ids = Document.objects.filter(
                project=project
            ).filter(
                Q(com_id__isnull=True) | Q(com_id='')
            ).count()
            
            if documents_without_com_ids > 0:
                projects_with_missing_com_ids.append(project)
        
        if self.verbose:
            self.stdout.write(f'Found {len(projects_with_missing_com_ids)} projects with missing COM IDs')
        
        return projects_with_missing_com_ids

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
                
                # Normalize document ID and validate it as barcode
                normalized_doc_id = normalize_document_id(document.doc_id)
                barcode_valid, validated_barcode = validate_barcode(normalized_doc_id)
                
                # Use validated barcode for COM ID lookup
                lookup_key = validated_barcode if barcode_valid else normalized_doc_id
                
                # Look up COM ID in mappings
                com_id = com_id_mappings.get(lookup_key)
                
                # If not found, try alternative lookup methods with original format
                if com_id is None:
                    # Try with original document ID (remove .pdf extension)
                    com_id = com_id_mappings.get(normalized_doc_id)
                    
                    # Try with numeric conversion for backward compatibility
                    if com_id is None:
                        try:
                            numeric_id = str(int(normalized_doc_id))
                            com_id = com_id_mappings.get(numeric_id)
                        except (ValueError, TypeError):
                            pass
                
                # Log validation results
                if not barcode_valid and normalized_doc_id and self.verbose:
                    self.stdout.write(f'    {document.doc_id}: Document ID is not a valid 16-digit barcode: "{normalized_doc_id}"')
                
                if com_id is not None:
                    # Validate COM ID before storing
                    com_id_valid, validated_com_id = validate_com_id(com_id)
                    if com_id_valid:
                        old_com_id = document.com_id
                        
                        if not self.dry_run:
                            document.com_id = validated_com_id
                            document.save()
                        
                        updated_count += 1
                        
                        if self.verbose:
                            if old_com_id is not None:
                                self.stdout.write(f'    {document.doc_id}: Updated COM ID {old_com_id} → {validated_com_id}')
                            else:
                                self.stdout.write(f'    {document.doc_id}: Set COM ID to {validated_com_id}')
                    else:
                        if self.verbose:
                            self.stdout.write(f'    {document.doc_id}: Invalid COM ID format "{com_id}". Expected 8 digits.')
                else:
                    if self.verbose:
                        self.stdout.write(f'    {document.doc_id}: No COM ID found in mappings (lookup_key: {lookup_key})')
                        
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
            elif file_extension in ['.xlsx', '.xlsm']:
                # Use openpyxl for .xlsx and .xlsm files
                data = self._read_xlsx_file(comlist_path)
            else:
                raise Exception(f'Unsupported file format: {file_extension}')
            
            if not data:
                return com_id_mappings
            
            # Skip header row if exists
            start_row = 1 if data and isinstance(data[0][0], str) and not str(data[0][0]).isdigit() else 0
            
            if self.verbose:
                self.stdout.write(f'  Processing {len(data)} rows, starting at row {start_row}')
            
            # Extract barcode and ComID pairs with robust validation
            for i in range(start_row, len(data)):
                if i < len(data) and len(data[i]) >= 2:
                    barcode_raw = data[i][0]
                    com_id_raw = data[i][1]
                    
                    # Skip empty rows
                    if barcode_raw is None and com_id_raw is None:
                        continue
                    
                    # Validate and normalize barcode (should be 16 digits)
                    barcode_valid, normalized_barcode = validate_barcode(barcode_raw)
                    if not barcode_valid:
                        # Fallback to original format for backward compatibility
                        normalized_barcode = normalize_document_id(str(barcode_raw)) if barcode_raw is not None else ""
                        if self.verbose:
                            self.stdout.write(f'    Row {i}: Invalid barcode format "{barcode_raw}". Expected 16 digits.')
                    
                    # Validate and normalize COM ID (should be 8 digits)
                    com_id_valid, normalized_com_id = validate_com_id(com_id_raw)
                    if not com_id_valid and com_id_raw is not None:
                        if self.verbose:
                            self.stdout.write(f'    Row {i}: Invalid COM ID format "{com_id_raw}". Expected 8 digits.')
                        continue  # Skip entries with invalid COM IDs
                    
                    if self.verbose:
                        self.stdout.write(f'    Row {i}: barcode: {barcode_raw} -> {normalized_barcode} (valid: {barcode_valid}), com_id: {com_id_raw} -> {normalized_com_id} (valid: {com_id_valid})')
                    
                    # Store mappings using normalized values
                    if normalized_barcode and normalized_com_id:
                        com_id_mappings[normalized_barcode] = normalized_com_id
                        
                        # Also store original barcode format for backward compatibility
                        if barcode_raw is not None:
                            original_barcode = str(barcode_raw).strip()
                            if original_barcode != normalized_barcode:
                                com_id_mappings[original_barcode] = normalized_com_id
            
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