"""
Handoff Service for Microfilm Processing System
Handles validation, file generation, and email delivery for completed projects.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

# Django imports for template rendering
from django.template.loader import render_to_string
from django.template import Context, Template

logger = logging.getLogger(__name__)

# Default email recipients
DEFAULT_EMAIL_RECIPIENTS = {
    'to': 'dilek.kursun@rolls-royce.com',
    'cc': 'thomas.lux@rolls-royce.com, jan.becker@rolls-royce.com'
}

@dataclass
class ValidationResult:
    """Result of validating a single document entry."""
    document_id: str
    roll: str
    barcode: str
    com_id: str
    temp_blip: str
    film_blip: Optional[str]
    status: str  # 'validated', 'warning', 'error', 'pending'
    message: Optional[str] = None
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    pages: Optional[int] = None

@dataclass
class ValidationSummary:
    """Summary of validation results."""
    total: int
    validated: int
    warnings: int
    errors: int
    pending: int

@dataclass
class FilmLogEntry:
    """Entry from a film log file."""
    roll_number: str
    document_id: str
    barcode: str
    blip: str
    start_frame: int
    end_frame: int
    pages: int
    timestamp: Optional[datetime] = None

class HandoffService:
    """Service for handling project handoff operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_project(self, project, validation_data: List[Dict]) -> Tuple[ValidationSummary, List[ValidationResult]]:
        """
        Validate project index against film log files.
        
        Args:
            project: Django Project model instance
            validation_data: List of temporary index entries to validate
            
        Returns:
            Tuple of (ValidationSummary, List[ValidationResult])
        """
        try:
            # Parse film log files
            film_logs = self._parse_film_logs(project)
            
            # Create lookup dictionary for fast access
            film_log_lookup = {}
            for log_entry in film_logs:
                key = f"{log_entry.roll_number}_{log_entry.document_id}"
                film_log_lookup[key] = log_entry
            
            # Validate each entry
            results = []
            summary = ValidationSummary(
                total=len(validation_data),
                validated=0,
                warnings=0,
                errors=0,
                pending=0
            )
            
            for item in validation_data:
                result = self._validate_single_entry(item, film_log_lookup)
                results.append(result)
                
                # Update summary
                if result.status == 'validated':
                    summary.validated += 1
                elif result.status == 'warning':
                    summary.warnings += 1
                elif result.status == 'error':
                    summary.errors += 1
                else:
                    summary.pending += 1
            
            self.logger.info(f"Validation complete for project {project.archive_id}: "
                           f"{summary.validated} validated, {summary.warnings} warnings, {summary.errors} errors")
            
            return summary, results
            
        except Exception as e:
            self.logger.error(f"Error validating project {project.archive_id}: {e}")
            raise
    
    def _parse_film_logs(self, project) -> List[FilmLogEntry]:
        """
        Parse film log files from project/.filmlogs/ directory.
        
        Args:
            project: Django Project model instance
            
        Returns:
            List of FilmLogEntry objects
        """
        film_logs = []
        
        if not project.project_path:
            self.logger.warning(f"No project path set for project {project.archive_id}")
            return film_logs
        
        filmlogs_dir = Path(project.project_path) / '.filmlogs'
        
        if not filmlogs_dir.exists():
            self.logger.warning(f"Film logs directory not found: {filmlogs_dir}")
            return film_logs
        
        # Find all log files (typically named like roll numbers: 10000001.txt, 10000002.txt, etc.)
        log_files = list(filmlogs_dir.glob('*.txt'))
        
        if not log_files:
            self.logger.warning(f"No log files found in {filmlogs_dir}")
            return film_logs
        
        for log_file in log_files:
            try:
                roll_number = log_file.stem  # Filename without extension
                entries = self._parse_single_log_file(log_file, roll_number)
                film_logs.extend(entries)
                self.logger.debug(f"Parsed {len(entries)} entries from {log_file}")
            except Exception as e:
                self.logger.error(f"Error parsing log file {log_file}: {e}")
                continue
        
        self.logger.info(f"Parsed {len(film_logs)} total entries from {len(log_files)} log files")
        return film_logs
    
    def _parse_single_log_file(self, log_file: Path, roll_number: str) -> List[FilmLogEntry]:
        """
        Parse a single film log file using the same logic as indexer_v2.py.
        
        Expected format:
        Rollennummer=10000001
        Datum/Zeit=5/21/2025 1:38:58 PM
        Benutzer=user1
        Computer=MICROFILM
        1427004807000278.pdf;0-1-0;0.00;1
        1427004807000278.pdf;0-1-1;0.01;2
        
        Args:
            log_file: Path to the log file
            roll_number: Roll number extracted from filename
            
        Returns:
            List of FilmLogEntry objects
        """
        entries = []
        
        try:
            # Use the same encoding detection logic as indexer_v2.py
            encoding = 'utf-16le'  # Primary encoding
            try:
                with open(log_file, 'r', encoding=encoding) as f:
                    lines = f.readlines()
            except UnicodeError:
                # Fallback to UTF-8 if UTF-16LE fails
                encoding = 'utf-8'
                with open(log_file, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                    
            self.logger.debug(f"Successfully read {log_file} with encoding: {encoding}")

            # Extract metadata from header (same as indexer_v2.py)
            roll = date = user = ""
            for line in lines[:10]:  # Check more lines for metadata
                if "Rollennummer=" in line:
                    roll = line.split("=")[1].strip()
                elif "Datum/Zeit=" in line:
                    date = line.split("=")[1].strip()
                elif "Benutzer=" in line:
                    user = line.split("=")[1].strip()
            
            if not roll:
                self.logger.warning(f"Could not extract roll number from {log_file}")
                roll = roll_number  # Use filename as fallback
            
            # Compile regex for better performance (same as indexer_v2.py)
            pdf_pattern = re.compile(r'^\d+\.pdf;')
            
            # Process page entries (same logic as indexer_v2.py)
            page_entries = []
            
            for line in lines[3:]:  # Skip header lines
                if not line.strip() or not pdf_pattern.match(line):
                    continue
                    
                parts = line.strip().split(";")
                if len(parts) < 2:
                    continue
                    
                document_filename = parts[0]  # e.g., "1427004807000278.pdf"
                blip_position = parts[1]      # e.g., "0-1-0"
                
                # Extract document ID (remove .pdf extension)
                barcode = document_filename.split(".")[0]
                
                page_entries.append({
                    'barcode': barcode,
                    'blip': blip_position,
                    'filename': document_filename
                })
            
            # Process blips using the same logic as indexer_v2.py
            processed_entries = self._process_blips_like_indexer(page_entries)
            
            # Create FilmLogEntry objects for each document
            for processed_entry in processed_entries:
                # Get document info
                barcode = processed_entry['barcode']
                processed_blip = processed_entry['blip']  # e.g., "0-2-21"
                
                # Count pages for this document in original entries
                doc_pages = len([e for e in page_entries if e['barcode'] == barcode])
                
                # Format blip like indexer_v2.py: roll-{doc_num:04}.{page_num:05}
                blip_parts = processed_blip.split('-')
                if len(blip_parts) >= 3:
                    try:
                        doc_num = int(blip_parts[1])
                        page_num = int(blip_parts[2])
                        formatted_blip = f"{roll}-{doc_num:04}.{page_num:05}"
                    except ValueError:
                        formatted_blip = f"{roll}-{processed_blip}"
                else:
                    formatted_blip = f"{roll}-{processed_blip}"
                
                # Calculate frame range (approximate)
                start_frame = (page_num - 1) * doc_pages + 1 if page_num > 0 else 1
                end_frame = start_frame + doc_pages - 1
                
                entry = FilmLogEntry(
                    roll_number=roll,
                    document_id=barcode,
                    barcode=barcode,
                    blip=formatted_blip,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    pages=doc_pages
                )
                entries.append(entry)
        
        except Exception as e:
            self.logger.error(f"Error reading log file {log_file}: {e}")
            raise
        
        self.logger.info(f"Parsed {len(entries)} document entries from {log_file}")
        return entries
    
    def _process_blips_like_indexer(self, page_entries: List[Dict]) -> List[Dict]:
        """
        Process blips using the same logic as indexer_v2.py process_blips method.
        
        Args:
            page_entries: List of page entry dictionaries
            
        Returns:
            List of processed entry dictionaries
        """
        from collections import defaultdict
        
        processed_entries = []
        total_pages = 0
        
        # Group by barcode (same as indexer_v2.py)
        barcode_groups = defaultdict(list)
        for entry in page_entries:
            barcode_groups[entry['barcode']].append(entry)
        
        # Process each document group (same as indexer_v2.py)
        for barcode, doc_entries in barcode_groups.items():
            first_entry = doc_entries[0]
            try:
                blip_parts = first_entry['blip'].split('-')
                if len(blip_parts) < 2:
                    self.logger.warning(f"Invalid blip format for barcode {barcode}: {first_entry['blip']}")
                    continue
                    
                doc_num = int(blip_parts[1])
                # Create new blip with cumulative page numbering (same as indexer_v2.py)
                new_blip = f"0-{doc_num}-{total_pages + 1}"
                
                processed_entries.append({
                    'barcode': barcode,
                    'blip': new_blip
                })
                
                total_pages += len(doc_entries)
                
            except (IndexError, ValueError) as e:
                self.logger.error(f"Error processing blip for barcode {barcode}: {e}")
                continue
        
        return processed_entries
    
    def _validate_single_entry(self, temp_entry: Dict, film_log_lookup: Dict[str, FilmLogEntry]) -> ValidationResult:
        """
        Validate a single temporary index entry against film logs.
        
        Args:
            temp_entry: Temporary index entry dictionary
            film_log_lookup: Dictionary of film log entries keyed by roll_document
            
        Returns:
            ValidationResult object
        """
        document_id = temp_entry.get('document_id', '')
        roll = temp_entry.get('roll', '')
        barcode = temp_entry.get('barcode', '')
        com_id = temp_entry.get('com_id', '')
        temp_blip = temp_entry.get('temp_blip', '')
        
        # Normalize document ID - remove .pdf extension if present for consistent matching
        normalized_doc_id = document_id.replace('.pdf', '') if document_id.endswith('.pdf') else document_id
        
        # Create lookup key using normalized document ID
        lookup_key = f"{roll}_{normalized_doc_id}"
        
        self.logger.debug(f"Looking up key: {lookup_key} (original doc_id: {document_id})")
        
        # Check if entry exists in film logs
        if lookup_key not in film_log_lookup:
            # Log available keys for debugging
            available_keys = list(film_log_lookup.keys())[:5]  # Show first 5 keys
            self.logger.debug(f"Key not found. Available keys (first 5): {available_keys}")
            
            return ValidationResult(
                document_id=document_id,
                roll=roll,
                barcode=barcode,
                com_id=com_id,
                temp_blip=temp_blip,
                film_blip=None,
                status='error',
                message=f'Document {normalized_doc_id} not found in film logs for roll {roll}'
            )
        
        film_entry = film_log_lookup[lookup_key]
        
        # Compare blips
        if temp_blip == film_entry.blip:
            # Perfect match
            return ValidationResult(
                document_id=document_id,
                roll=roll,
                barcode=barcode,
                com_id=com_id,
                temp_blip=temp_blip,
                film_blip=film_entry.blip,
                status='validated',
                message='Blip matches exactly',
                start_frame=film_entry.start_frame,
                end_frame=film_entry.end_frame,
                pages=film_entry.pages
            )
        else:
            # Check if it's a minor difference (warning) or major difference (error)
            similarity = self._calculate_blip_similarity(temp_blip, film_entry.blip)
            
            if similarity > 0.8:  # Minor difference - warning
                return ValidationResult(
                    document_id=document_id,
                    roll=roll,
                    barcode=barcode,
                    com_id=com_id,
                    temp_blip=temp_blip,
                    film_blip=film_entry.blip,
                    status='warning',
                    message=f'Blip mismatch: expected {temp_blip}, found {film_entry.blip}',
                    start_frame=film_entry.start_frame,
                    end_frame=film_entry.end_frame,
                    pages=film_entry.pages
                )
            else:  # Major difference - error
                return ValidationResult(
                    document_id=document_id,
                    roll=roll,
                    barcode=barcode,
                    com_id=com_id,
                    temp_blip=temp_blip,
                    film_blip=film_entry.blip,
                    status='error',
                    message=f'Significant blip mismatch: expected {temp_blip}, found {film_entry.blip}',
                    start_frame=film_entry.start_frame,
                    end_frame=film_entry.end_frame,
                    pages=film_entry.pages
                )
    
    def _calculate_blip_similarity(self, blip1: str, blip2: str) -> float:
        """
        Calculate similarity between two blip strings.
        
        Args:
            blip1: First blip string
            blip2: Second blip string
            
        Returns:
            Similarity score between 0 and 1
        """
        if blip1 == blip2:
            return 1.0
        
        # Simple similarity based on common characters and structure
        if len(blip1) == 0 or len(blip2) == 0:
            return 0.0
        
        # Check if they have the same structure (roll-doc.frame format)
        pattern = r'^(\d+)-(\d+)\.(\d+)\.(\d+)$'
        match1 = re.match(pattern, blip1)
        match2 = re.match(pattern, blip2)
        
        if match1 and match2:
            # Compare components
            roll1, doc1, frame1, subframe1 = match1.groups()
            roll2, doc2, frame2, subframe2 = match2.groups()
            
            # Same roll and document, different frame numbers = high similarity
            if roll1 == roll2 and doc1 == doc2:
                frame_diff = abs(int(frame1) - int(frame2))
                if frame_diff <= 5:  # Within 5 frames
                    return 0.9
                elif frame_diff <= 10:  # Within 10 frames
                    return 0.8
                else:
                    return 0.5
        
        # Fallback: simple string similarity
        common_chars = sum(1 for a, b in zip(blip1, blip2) if a == b)
        max_length = max(len(blip1), len(blip2))
        return common_chars / max_length if max_length > 0 else 0.0
    
    def generate_handoff_files(self, project, validated_results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Generate the final handoff files (scan.xlsx and scan.dat).
        
        Args:
            project: Django Project model instance
            validated_results: List of ValidationResult objects
            
        Returns:
            Dictionary with file paths and metadata
        """
        try:
            # Create export directory
            project_path = Path(project.project_path) if project.project_path else Path.cwd()
            export_dir = project_path / '.export'
            export_dir.mkdir(exist_ok=True)
            
            # Filter successful validations (validated + warnings)
            valid_entries = [r for r in validated_results if r.status in ['validated', 'warning']]
            
            if not valid_entries:
                raise ValueError("No valid entries to export")
            
            # Generate files
            excel_path = self._generate_excel_file(export_dir, valid_entries, project)
            dat_path = self._generate_dat_file(export_dir, valid_entries, project)
            
            # Get file sizes
            excel_size = excel_path.stat().st_size if excel_path.exists() else 0
            dat_size = dat_path.stat().st_size if dat_path.exists() else 0
            
            self.logger.info(f"Generated handoff files for project {project.archive_id}: "
                           f"Excel ({excel_size} bytes), DAT ({dat_size} bytes)")
            
            return {
                'excel_path': str(excel_path),
                'dat_path': str(dat_path),
                'excel_size': excel_size,
                'dat_size': dat_size,
                'entries_count': len(valid_entries),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating handoff files for project {project.archive_id}: {e}")
            raise
    
    def _generate_excel_file(self, export_dir: Path, entries: List[ValidationResult], project) -> Path:
        """
        Generate Excel file with validation results.
        
        Args:
            export_dir: Directory to save the file
            entries: List of ValidationResult objects
            project: Django Project model instance
            
        Returns:
            Path to the generated Excel file
        """
        excel_path = export_dir / 'blips.xlsx'
        
        # Prepare data for DataFrame with only required columns
        data = []
        for entry in entries:
            # Remove .pdf extension from barcode if present
            barcode = entry.barcode.replace('.pdf', '') if entry.barcode.endswith('.pdf') else entry.barcode
            
            data.append({
                'Barcode': barcode,
                'Bildnummer': entry.com_id,
                'Blipindex': entry.film_blip or entry.temp_blip
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Sort numerically by barcode (convert to int for proper numeric sorting)
        try:
            df['barcode_numeric'] = pd.to_numeric(df['Barcode'], errors='coerce')
            df = df.sort_values('barcode_numeric').drop('barcode_numeric', axis=1)
        except:
            # Fallback to string sorting if numeric conversion fails
            df = df.sort_values('Barcode')
        
        # Save to Excel with specified headers only
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # Write main data sheet with only the required columns
            df.to_excel(writer, sheet_name='Index', index=False)
            
            # Format the sheet
            workbook = writer.book
            worksheet = writer.sheets['Index']
            
            # Add header formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Apply header formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.set_column(i, i, min(max_length + 2, 50))
        
        return excel_path
    
    def _generate_dat_file(self, export_dir: Path, entries: List[ValidationResult], project) -> Path:
        """
        Generate fixed-width DAT file for legacy systems.
        
        Args:
            export_dir: Directory to save the file
            entries: List of ValidationResult objects
            project: Django Project model instance
            
        Returns:
            Path to the generated DAT file
        """
        dat_path = export_dir / 'scan.dat'
        
        # Prepare entries for sorting
        entries_for_sorting = []
        for entry in entries:
            # Remove .pdf extension from barcode if present
            barcode = entry.barcode.replace('.pdf', '') if entry.barcode.endswith('.pdf') else entry.barcode
            entries_for_sorting.append({
                'barcode': barcode,
                'com_id': entry.com_id,
                'blip': entry.film_blip or entry.temp_blip
            })
        
        # Sort numerically by barcode
        try:
            sorted_entries = sorted(entries_for_sorting, key=lambda x: int(x['barcode']) if x['barcode'].isdigit() else float('inf'))
        except:
            # Fallback to string sorting if numeric conversion fails
            sorted_entries = sorted(entries_for_sorting, key=lambda x: x['barcode'])
        
        with open(dat_path, 'w', encoding='utf-8') as f:
            # Write only data lines in fixed-width format (no header comments)
            for entry in sorted_entries:
                # Format: COM_ID (13 chars) + BARCODE (48 chars) + BLIP
                # Ensure com_id and barcode are strings before calling ljust
                com_id = str(entry['com_id'] or '').ljust(13)[:13]
                barcode = str(entry['barcode'] or '').ljust(48)[:48]
                blip = entry['blip'] or ''
                
                line = f"{com_id}{barcode}{blip}\n"
                f.write(line)
        
        return dat_path
    
    def send_handoff_email(self, project, email_data: Dict[str, Any], file_paths: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send handoff email with generated files using Outlook COM interface.
        
        Args:
            project: Django Project model instance
            email_data: Dictionary with email details (to, cc, subject, body, use_custom_body)
            file_paths: Dictionary with file paths from generate_handoff_files
            
        Returns:
            Dictionary with send result
        """
        try:
            # Handle default recipients more intelligently
            # Only set defaults if the field is completely missing (None), not if it's empty string
            if email_data.get('to') is None:
                email_data['to'] = DEFAULT_EMAIL_RECIPIENTS['to']
                self.logger.debug("Using default TO recipients (field was not provided)")
            elif not email_data.get('to').strip():
                # TO field is required - cannot be empty
                self.logger.error("TO field cannot be empty")
                return {
                    'success': False,
                    'error': 'TO field is required and cannot be empty',
                    'method': 'validation_failed'
                }
            
            # For CC field: None = use default, empty string = no CC recipients
            if email_data.get('cc') is None:
                email_data['cc'] = DEFAULT_EMAIL_RECIPIENTS['cc']
                self.logger.debug("Using default CC recipients (field was not provided)")
            elif not email_data.get('cc').strip():
                # User intentionally left CC empty - respect that choice
                email_data['cc'] = ''
                self.logger.debug("CC field intentionally left empty by user")
            
            self.logger.info(f"Final recipients - To: {email_data.get('to')}, CC: {email_data.get('cc') or 'None'}")
            
            # Use custom body if provided and flagged, otherwise generate from template
            if email_data.get('use_custom_body') and email_data.get('body'):
                email_body = email_data['body']
                self.logger.info(f"Using custom email body for project {project.archive_id}")
            else:
                email_body = self._generate_email_body(project, file_paths)
                self.logger.info(f"Generated email body using template for project {project.archive_id}")
            
            self.logger.debug(f"Email recipients - To: {email_data.get('to')}, CC: {email_data.get('cc')}")
            
            # Import win32com for Outlook automation
            try:
                import win32com.client as win32
                import pythoncom
            except ImportError:
                self.logger.error("win32com not available - cannot send emails")
                return {
                    'success': False,
                    'error': 'Outlook COM interface not available. Please ensure Microsoft Outlook is installed and accessible.',
                    'method': 'outlook_com_failed'
                }
            
            # Initialize COM
            try:
                pythoncom.CoInitialize()
                self.logger.debug("COM initialized successfully")
            except Exception as com_error:
                self.logger.warning(f"COM already initialized or initialization failed: {com_error}")
                # Continue anyway as COM might already be initialized
            
            # Create Outlook application object
            outlook = win32.Dispatch('outlook.application')
            
            try:
                # Create mail item
                mail = outlook.CreateItem(0)  # 0 = olMailItem
                
                # Set recipients - handle multiple recipients properly
                to_recipients = [email.strip() for email in email_data.get('to', '').split(',') if email.strip()]
                cc_recipients = [email.strip() for email in email_data.get('cc', '').split(',') if email.strip()]
                
                # Add TO recipients
                for recipient in to_recipients:
                    try:
                        mail.Recipients.Add(recipient)
                        self.logger.debug(f"Added TO recipient: {recipient}")
                    except Exception as e:
                        self.logger.warning(f"Failed to add TO recipient {recipient}: {e}")
                
                # Add CC recipients
                for recipient in cc_recipients:
                    try:
                        recipient_obj = mail.Recipients.Add(recipient)
                        recipient_obj.Type = 2  # 2 = olCC
                        self.logger.debug(f"Added CC recipient: {recipient}")
                    except Exception as e:
                        self.logger.warning(f"Failed to add CC recipient {recipient}: {e}")
                
                # Resolve all recipients
                try:
                    mail.Recipients.ResolveAll()
                    self.logger.debug("All recipients resolved successfully")
                except Exception as e:
                    self.logger.warning(f"Some recipients could not be resolved: {e}")
                    # Continue anyway - Outlook might still send the email
                
                # Set subject and body
                mail.Subject = email_data.get('subject', f'Microfilm Project Handoff - {project.archive_id}')
                mail.HTMLBody = email_body
                
                # Add attachments
                attachments_added = []
                for file_type, file_path in file_paths.items():
                    if file_type.endswith('_path') and file_path and Path(file_path).exists():
                        mail.Attachments.Add(str(file_path))
                        attachments_added.append(Path(file_path).name)
                        self.logger.debug(f"Added attachment: {file_path}")
                
                # Send the email
                mail.Display(0)
                #mail.Send()
                self.logger.info(f"Handoff email sent successfully via Outlook for project {project.archive_id} "
                               f"to {len(to_recipients)} recipients with {len(attachments_added)} attachments")
                
                return {
                    'success': True,
                    'message': f'Email sent successfully via Outlook to {", ".join(to_recipients)}',
                    'sent_at': datetime.now().isoformat(),
                    'attachments': attachments_added,
                    'method': 'outlook_com',
                    'recipients': {
                        'to': ', '.join(to_recipients),
                        'cc': ', '.join(cc_recipients)
                    },
                    'body_type': 'custom' if email_data.get('use_custom_body') else 'template'
                }
                
            except Exception as e:
                self.logger.error(f"Error with Outlook COM operations for project {project.archive_id}: {e}")
                return {
                    'success': False,
                    'error': f'Error sending handoff email: {str(e)}',
                    'method': 'outlook_com_failed'
                }
            finally:
                # Clean up COM
                try:
                    pythoncom.CoUninitialize()
                    self.logger.debug("COM uninitialized successfully")
                except Exception as cleanup_error:
                    self.logger.warning(f"Error during COM cleanup: {cleanup_error}")
                    
        except Exception as e:
            self.logger.error(f"Error sending handoff email for project {project.archive_id}: {e}")
            return {
                'success': False,
                'error': f'Error sending handoff email: {str(e)}',
                'method': 'outlook_com_failed'
            }
    
    def _generate_email_body(self, project, file_paths: Dict[str, Any]) -> str:
        """
        Generate email body using Django template.
        
        Args:
            project: Django Project model instance
            file_paths: Dictionary with file paths and metadata
            
        Returns:
            Rendered HTML email body
        """
        try:
            # Get film numbers from project
            film_numbers = self._get_project_roll_numbers(project)
            
            # Prepare template context
            context = {
                'project': project,
                'film_numbers': film_numbers,
                'file_paths': file_paths,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Render template using the original professional signature template
            email_body = render_to_string('microapp/handoff/email/signature_template.html', context)
            return email_body
            
        except Exception as e:
            self.logger.error(f"Error generating email body: {e}")
            # Fallback to simple text
            return self._generate_default_email_body(project, file_paths)
    
    def _get_project_roll_numbers(self, project) -> str:
        """
        Get formatted film numbers for the project.
        
        Args:
            project: Django Project model instance
            
        Returns:
            Comma-separated string of film numbers
        """
        try:
            # Get all rolls for this project, ordered by film_number or roll_number
            rolls = project.rolls.all().order_by('film_number', 'roll_number')
            
            # Prefer film_number, fallback to roll_number
            film_numbers = []
            for roll in rolls:
                if roll.film_number:
                    film_numbers.append(roll.film_number)
                elif roll.roll_number:
                    film_numbers.append(roll.roll_number)
            
            if film_numbers:
                return ', '.join(film_numbers)
            else:
                return 'N/A'
                
        except Exception as e:
            self.logger.error(f"Error getting film numbers for project {project.archive_id}: {e}")
            return 'N/A'
    
    def _generate_default_email_body(self, project, file_paths: Dict[str, Any]) -> str:
        """
        Generate default email body for handoff emails.
        
        Args:
            project: Django Project model instance
            file_paths: Dictionary with file paths and metadata
            
        Returns:
            Default email body text
        """
        film_numbers = self._get_project_roll_numbers(project)
        
        return f"""Dear Team,

Please find attached the final index files for the completed microfilm project.

Project Details:
- Archive ID: {project.archive_id}
- Project Name: {project.name or 'N/A'}
- Document Type: {project.doc_type or 'Documents'}
- Location: {project.location or 'N/A'}
- Film Numbers: {film_numbers}
- Total Documents: {file_paths.get('entries_count', 'N/A')}
- Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Attached Files:
- blips.xlsx (Excel format index - {file_paths.get('excel_size', 0)} bytes)
- scan.dat (Legacy format index - {file_paths.get('dat_size', 0)} bytes)

The project has been successfully filmed, developed, validated, and is ready for final processing.

Best regards,
Iron Mountain Microfilm Team

---
This email was generated automatically by the Microfilm Processing System.
""" 