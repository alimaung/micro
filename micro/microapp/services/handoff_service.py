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
import win32com.client as win32
import requests
import random

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
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%d%m%y%H%M')
        archive_id = project.archive_id or 'PROJECT'
        excel_path = export_dir / f'{archive_id}_blips_{timestamp}.xlsx'
        
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
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%d%m%y%H%M')
        archive_id = project.archive_id or 'PROJECT'
        dat_path = export_dir / f'{archive_id}_scan_{timestamp}.dat'
        
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
        Send handoff email using form data to populate signature placeholders.
        
        Args:
            project: Django Project model instance
            email_data: Dictionary with form data (to, cc, subject, archive_id, film_numbers, custom_message, use_form_data)
            file_paths: Dictionary with file paths from generate_handoff_files
            
        Returns:
            Dictionary with send result
        """
        try:
            # Handle default recipients
            if not email_data.get('to'):
                email_data['to'] = 'dilek.kursun@rolls-royce.com'
            
            if not email_data.get('cc'):
                email_data['cc'] = 'thomas.lux@rolls-royce.com, jan.becker@rolls-royce.com'

            # Validate email addresses before proceeding
            def validate_email_list(email_string):
                if not email_string:
                    return []
                # Handle both comma and semicolon separators (convert commas to semicolons for Outlook)
                # First normalize by replacing semicolons with commas for consistent processing
                normalized_string = email_string.replace(';', ',')
                emails = [email.strip() for email in normalized_string.split(',') if email.strip()]
                valid_emails = []
                for email in emails:
                    if '@' in email and '.' in email.split('@')[1]:
                        valid_emails.append(email)
                    else:
                        self.logger.warning(f"Invalid email address format: {email}")
                return valid_emails
            
            to_emails = validate_email_list(email_data['to'])
            cc_emails = validate_email_list(email_data.get('cc', ''))
            
            # Log email processing for debugging
            self.logger.info(f"Processing emails - TO: {to_emails}, CC: {cc_emails}")
            
            if not to_emails:
                raise ValueError("No valid TO email addresses provided")
            
            # Update email_data with validated emails using semicolons for Outlook
            email_data['to'] = '; '.join(to_emails)
            if cc_emails:
                email_data['cc'] = '; '.join(cc_emails)
                self.logger.info(f"CC emails processed: {len(cc_emails)} recipients - {email_data['cc']}")
            else:
                email_data['cc'] = ''
                self.logger.info("No CC emails provided")

            # Initialize Outlook
            try:
                import pythoncom
                # Initialize COM for this thread
                pythoncom.CoInitialize()
                self.logger.debug("COM initialized successfully")
            except Exception as com_init_error:
                self.logger.warning(f"COM initialization warning: {com_init_error}")
                # Continue anyway as COM might already be initialized
            
            outlook = None
            mail = None
            
            try:
                outlook = win32.Dispatch('Outlook.Application')
                mail = outlook.CreateItem(0)  # 0 = Mail item
                
                # Set basic email properties
                mail.To = email_data['to']
                if email_data.get('cc'):
                    mail.CC = email_data['cc']
                mail.Subject = email_data['subject']
                
                # Try to resolve recipients before proceeding
                try:
                    # This will attempt to resolve all recipients
                    mail.Recipients.ResolveAll()
                    self.logger.info("All recipients resolved successfully")
                except Exception as resolve_error:
                    self.logger.warning(f"Some recipients could not be resolved: {resolve_error}")
                    # Continue anyway - Outlook might still send the email
                    
                    # Alternative approach: Add recipients manually and mark as resolved
                    try:
                        mail.Recipients.RemoveAll()  # Clear existing recipients
                        
                        # Add TO recipients
                        to_emails = [email.strip() for email in email_data['to'].replace(';', ',').split(',') if email.strip()]
                        for email_addr in to_emails:
                            recipient = mail.Recipients.Add(email_addr)
                            recipient.Type = 1  # olTo
                            recipient.Resolve()  # Try to resolve individual recipient
                            self.logger.debug(f"Added TO recipient: {email_addr}")
                        
                        # Add CC recipients
                        if email_data.get('cc'):
                            cc_emails = [email.strip() for email in email_data['cc'].replace(';', ',').split(',') if email.strip()]
                            self.logger.info(f"Adding {len(cc_emails)} CC recipients: {cc_emails}")
                            for email_addr in cc_emails:
                                recipient = mail.Recipients.Add(email_addr)
                                recipient.Type = 2  # olCC
                                recipient.Resolve()  # Try to resolve individual recipient
                                self.logger.debug(f"Added CC recipient: {email_addr}")
                        
                        self.logger.info("Recipients added manually")
                    except Exception as manual_error:
                        self.logger.warning(f"Manual recipient resolution also failed: {manual_error}")
                        # Continue with original recipients
                        mail.To = email_data['to']
                        if email_data.get('cc'):
                            mail.CC = email_data['cc']
                
                # Get signature with placeholders using GetInspector trick
                mail.GetInspector  # This triggers Outlook to add the default signature
                
                # Get the signature HTML (now contains default signature)
                signature_html = mail.HTMLBody
                
                # Prepare placeholder values
                archive_id = email_data.get('archive_id') or project.archive_id
                film_numbers = email_data.get('film_numbers', '')
                
                # If film numbers are empty, get them from the project
                if not film_numbers or film_numbers.strip() == '':
                    film_numbers = self._get_project_roll_numbers(project)
                
                custom_message = email_data.get('custom_message', '')
                
                # Generate timestamp for filenames
                timestamp = datetime.now().strftime('%d%m%y%H%M')
                
                # Get random quote
                random_quote = self._get_random_quote()
                
                # Replace signature placeholders
                if signature_html:
                    # Replace XXX with archive_id (appears in multiple places)
                    signature_html = signature_html.replace('XXX', archive_id)
                    
                    # Replace YYY with film numbers
                    signature_html = signature_html.replace('YYY', film_numbers)
                    
                    # Replace DDMMYYHHMM with actual timestamp
                    signature_html = signature_html.replace('DDMMYYHHMM', timestamp)
                    
                    # Replace QQQ with random quote
                    signature_html = signature_html.replace('QQQ', random_quote)
                    
                    # Replace CCC with custom message or em dash if empty
                    if custom_message and custom_message.strip():
                        # Convert line breaks to HTML breaks for proper display
                        formatted_message = custom_message.strip().replace('\n', '<br>')
                        signature_html = signature_html.replace('CCC', formatted_message)
                    else:
                        # Replace CCC placeholder with em dash if no custom message
                        signature_html = signature_html.replace('CCC', '—')
                    
                    self.logger.debug(f"Replaced signature placeholders: XXX→{archive_id}, YYY→{film_numbers}, DDMMYYHHMM→{timestamp}, QQQ→{random_quote[:50]}..., CCC→{custom_message[:30] if custom_message else 'em dash'}...")
                    
                    mail.HTMLBody = signature_html
                
                # Add attachments if available
                if file_paths:
                    # Handle both old and new file_paths structure
                    if isinstance(file_paths, dict):
                        # New structure from generate_handoff_files
                        if 'excel_path' in file_paths and os.path.exists(file_paths['excel_path']):
                            mail.Attachments.Add(file_paths['excel_path'])
                            self.logger.info(f"Added Excel attachment: {file_paths['excel_path']}")
                        
                        if 'dat_path' in file_paths and os.path.exists(file_paths['dat_path']):
                            mail.Attachments.Add(file_paths['dat_path'])
                            self.logger.info(f"Added DAT attachment: {file_paths['dat_path']}")
                        
                        # Only process legacy structure if new structure keys are not present
                        elif not ('excel_path' in file_paths or 'dat_path' in file_paths):
                            # Legacy structure support
                            for file_type, file_info in file_paths.items():
                                if isinstance(file_info, dict) and 'path' in file_info:
                                    file_path = file_info['path']
                                    if os.path.exists(file_path):
                                        mail.Attachments.Add(file_path)
                                        self.logger.info(f"Added legacy attachment: {file_path}")
                                elif isinstance(file_info, str) and os.path.exists(file_info):
                                    mail.Attachments.Add(file_info)
                                    self.logger.info(f"Added string path attachment: {file_info}")
                
                # Send the email
                try:
                    mail.Send()
                    #mail.Display(True)
                    self.logger.info(f"Email sent successfully for project {project.archive_id}")
                    send_method = "sent"
                except Exception as send_error:
                    self.logger.warning(f"Failed to send email directly: {send_error}")
                    # Fallback: Display the email for manual sending
                    try:
                        mail.Display(True)  # True = modal dialog
                        self.logger.info(f"Email displayed for manual sending for project {project.archive_id}")
                        send_method = "displayed"
                    except Exception as display_error:
                        self.logger.error(f"Failed to display email: {display_error}")
                        raise Exception(f"Could not send or display email: {send_error}")

                return {
                    'success': True,
                    'message': f'Email {"sent automatically" if send_method == "sent" else "opened in Outlook for manual sending"} to {email_data["to"]}',
                    'method': send_method,
                    'archive_id': archive_id,
                    'film_numbers': film_numbers
                }
                
            except Exception as outlook_error:
                self.logger.error(f"Outlook COM error: {outlook_error}")
                raise
            finally:
                # Clean up COM
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                    self.logger.debug("COM uninitialized successfully")
                except Exception as cleanup_error:
                    self.logger.warning(f"COM cleanup warning: {cleanup_error}")
            
        except Exception as e:
            error_msg = f"Failed to send email for project {project.archive_id}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg
            }

    def _customize_signature_content(self, signature_html: str, project, custom_message: str = None) -> str:
        """
        Customize signature content by replacing placeholders with project data.
        
        Args:
            signature_html: Original signature HTML from Outlook
            project: Django Project model instance
            custom_message: Optional custom message to replace CCC placeholder
            
        Returns:
            Customized signature HTML
        """
        try:
            if not signature_html:
                return signature_html
            
            # Generate timestamp for filenames
            timestamp = self._generate_timestamp()
            
            # Get film numbers
            film_numbers = self._get_project_roll_numbers(project)
            
            # Get archive ID
            archive_id = str(project.archive_id) if hasattr(project, 'archive_id') and project.archive_id else 'UNKNOWN'
            
            # Replace placeholders in signature
            customized_html = signature_html
            
            # Replace XXX with archive_id (appears in multiple places)
            customized_html = customized_html.replace('XXX', archive_id)
            
            # Replace YYY with film numbers
            if film_numbers:
                customized_html = customized_html.replace('YYY', film_numbers)
            else:
                customized_html = customized_html.replace('YYY', 'N/A')
            
            # Replace DDMMYYHHMM with actual timestamp
            customized_html = customized_html.replace('DDMMYYHHMM', timestamp)
            
            # Replace QQQ with random quote
            random_quote = self._get_random_quote()
            customized_html = customized_html.replace('QQQ', random_quote)
            
            # Replace CCC with custom message or em dash if empty
            if custom_message and custom_message.strip():
                # Convert line breaks to HTML breaks for proper display
                formatted_message = custom_message.strip().replace('\n', '<br>')
                customized_html = customized_html.replace('CCC', formatted_message)
            else:
                # Replace CCC placeholder with em dash if no custom message
                customized_html = customized_html.replace('CCC', '—')
            
            self.logger.debug(f"Customized signature placeholders: XXX -> {archive_id}, YYY -> {film_numbers or 'N/A'}, DDMMYYHHMM -> {timestamp}, QQQ -> {random_quote[:50]}..., CCC -> {custom_message[:30] if custom_message else 'em dash'}...")
            
            return customized_html
            
        except Exception as e:
            self.logger.error(f"Error customizing signature content: {e}")
            return signature_html  # Return original if customization fails

    def _generate_timestamp(self) -> str:
        """
        Generate timestamp in DDMMYYHHMM format for filenames.
        
        Returns:
            Formatted timestamp string
        """
        return datetime.now().strftime('%d%m%y%H%M')
    
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

    def _get_random_quote(self) -> str:
        """
        Fetch a random inspirational quote from an API or fallback to local quotes.
        Supports both English and German with specific categories and length limits.
        
        Returns:
            Random quote string
        """
        # Randomly choose language
        language = random.choice(['en', 'de'])
        
        # Define categories mapping
        categories = [
            'business', 'success', 'motivational', 'inspirational', 
            'wisdom', 'philosophy', 'work', 'productivity', 'famous-people',
            'humor', 'education', 'learning'
        ]
        
        try:
            # Try quotable.io for English quotes
            if language == 'en':
                category = random.choice(['wisdom', 'success', 'motivational', 'famous-quotes'])
                max_length = random.choice([50, 150])  # short or medium
                
                response = requests.get(
                    'https://api.quotable.io/random',
                    params={
                        'tags': category,
                        'maxLength': max_length
                    },
                    timeout=3
                )
                
                if response.status_code == 200:
                    data = response.json()
                    quote = f'"{data["content"]}" - {data["author"]}'
                    self.logger.debug(f"Fetched English quote from API: {quote}")
                    return quote
            
            # Try alternative API for German quotes
            else:
                # For German, we'll use a different approach or fallback faster
                pass
                
        except Exception as api_error:
            self.logger.warning(f"Failed to fetch quote from API: {api_error}")
        
        # Enhanced fallback quotes in both languages
        english_quotes = [
            '"The only way to do great work is to love what you do." - Steve Jobs',
            '"Innovation distinguishes between a leader and a follower." - Steve Jobs',
            '"Quality is not an act, it is a habit." - Aristotle',
            '"Excellence is never an accident." - Aristotle',
            '"Success is not final, failure is not fatal." - Winston Churchill',
            '"The only impossible journey is the one you never begin." - Tony Robbins',
            '"In the middle of difficulty lies opportunity." - Albert Einstein',
            '"Believe you can and you\'re halfway there." - Theodore Roosevelt',
            '"Knowledge is power." - Francis Bacon',
            '"The best investment you can make is in yourself." - Warren Buffett',
            '"Productivity is never an accident." - Paul J. Meyer',
            '"Laughter is the best medicine." - Proverb',
            '"A goal without a plan is just a wish." - Antoine de Saint-Exupéry',
            '"The expert in anything was once a beginner." - Helen Hayes'
        ]
        
        german_quotes = [
            '"Erfolg ist die Fähigkeit, von einem Misserfolg zum anderen zu gehen, ohne seine Begeisterung zu verlieren." - Winston Churchill',
            '"Das Geheimnis des Erfolgs ist anzufangen." - Mark Twain',
            '"Wissen ist Macht." - Francis Bacon',
            '"Qualität ist kein Zufall." - Aristoteles',
            '"Innovation unterscheidet zwischen einem Anführer und einem Nachfolger." - Steve Jobs',
            '"Der beste Weg, die Zukunft vorherzusagen, ist, sie zu erschaffen." - Peter Drucker',
            '"Bildung ist die mächtigste Waffe, um die Welt zu verändern." - Nelson Mandela',
            '"Lachen ist die beste Medizin." - Sprichwort',
            '"Ein Ziel ohne Plan ist nur ein Wunsch." - Antoine de Saint-Exupéry',
            '"Produktivität ist niemals ein Zufall." - Paul J. Meyer',
            '"In der Mitte der Schwierigkeit liegt die Möglichkeit." - Albert Einstein',
            '"Weisheit ist nicht das Ergebnis der Schulbildung, sondern des lebenslangen Versuchs, sie zu erwerben." - Albert Einstein',
            '"Der Experte in allem war einmal ein Anfänger." - Helen Hayes',
            '"Glaube an dich selbst und du bist schon zur Hälfte da." - Theodore Roosevelt',
            # Business/Success quotes
            '"Geschäfte sind wie ein Rad - sie müssen sich bewegen oder sie fallen um." - Henry Ford',
            '"Der Kunde ist König, aber der Service ist das Königreich." - Unbekannt',
            '"Erfolg besteht darin, dass man genau die Fähigkeiten hat, die im Moment gefragt sind." - Henry Ford',
            '"Wer aufhört zu werben, um Geld zu sparen, kann ebenso seine Uhr anhalten, um Zeit zu sparen." - Henry Ford',
            # Motivational/Inspirational quotes
            '"Träume nicht dein Leben, sondern lebe deinen Traum." - Mark Twain',
            '"Was uns nicht umbringt, macht uns stärker." - Friedrich Nietzsche',
            '"Mut ist nicht die Abwesenheit von Furcht, sondern die Erkenntnis, dass etwas anderes wichtiger ist als die Furcht." - Ambrose Redmoon',
            '"Der Weg ist das Ziel." - Konfuzius',
            # Wisdom/Philosophy quotes
            '"Ich weiß, dass ich nichts weiß." - Sokrates',
            '"Die Zeit heilt alle Wunden." - Sprichwort',
            '"Wer anderen eine Grube gräbt, fällt selbst hinein." - Sprichwort',
            '"Aller Anfang ist schwer." - Sprichwort',
            # Work/Productivity quotes
            '"Arbeit ist das halbe Leben, und die andere Hälfte auch." - Unbekannt',
            '"Fleiß ist des Glückes Vater." - Sprichwort',
            '"Ohne Fleiß kein Preis." - Sprichwort',
            '"Übung macht den Meister." - Sprichwort',
            # Famous People quotes
            '"Phantasie ist wichtiger als Wissen." - Albert Einstein',
            '"Habe Mut, dich deines eigenen Verstandes zu bedienen!" - Immanuel Kant',
            '"Die Musik drückt das aus, was nicht gesagt werden kann und worüber zu schweigen unmöglich ist." - Victor Hugo',
            # Humor quotes
            '"Humor ist der Knopf, der verhindert, dass uns der Kragen platzt." - Joachim Ringelnatz',
            '"Lächeln ist die eleganteste Art, seinen Gegnern die Zähne zu zeigen." - Werner Finck'
        ]
        
        # Choose quotes based on intended language
        if language == 'de':
            quote = random.choice(german_quotes)
            self.logger.debug(f"Using fallback German quote: {quote}")
        else:
            quote = random.choice(english_quotes)
            self.logger.debug(f"Using fallback English quote: {quote}")
            
        return quote 