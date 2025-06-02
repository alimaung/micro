import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import win32com.client
import os
from collections import defaultdict
import concurrent.futures
import pythoncom
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def RGB(r, g, b):
    """Convert RGB values to BGR format used by Excel."""
    return r + (g * 256) + (b * 256 * 256)

@dataclass
class DocumentMetadata:
    roll: str
    date: str
    user: str

@dataclass
class PageEntry:
    barcode: str
    blip: str
    com_id: Optional[str] = None

class FileProcessor:
    def __init__(self, txt_path: str, xlsx_path: str):
        self.txt_path = Path(txt_path)
        self.xlsx_path = Path(xlsx_path)
        self.validate_files()

    def validate_files(self) -> None:
        """Validate that input files exist and have correct extensions."""
        logger.info(f"validating files")
        if self.txt_path.name:  # Only validate txt_path if it's provided
            if not self.txt_path.exists():
                raise FileNotFoundError(f"Text file not found: {self.txt_path}")
            if self.txt_path.suffix.lower() != '.txt':
                raise ValueError(f"Expected .txt file, got: {self.txt_path}")

        if self.xlsx_path.name:  # Only validate xlsx_path if it's provided
            if not self.xlsx_path.exists():
                raise FileNotFoundError(f"Excel file not found: {self.xlsx_path}")
            if self.xlsx_path.suffix.lower() not in ['.xls', '.xlsx']:
                raise ValueError(f"Expected .xls/.xlsx file, got: {self.xlsx_path}")

    def extract_xlsx(self) -> Dict[str, str]:
        """Extract barcode to com_id mapping from Excel file."""
        logger.info("extract xlsx")
        excel = None
        try:
            # Initialize COM for this thread
            pythoncom.CoInitialize()
            
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            
            wb = excel.Workbooks.Open(str(self.xlsx_path))
            sheet = wb.Sheets(1)
            
            # Read all values at once into an array for better performance
            data_range = sheet.UsedRange
            values = data_range.Value
            
            # Process values in memory
            mapping = {
                str(row[0]).strip(): str(row[1]).strip()
                for row in values
                if row[0] and row[1]
            }
            
            wb.Close(False)
            return mapping
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise
        finally:
            if excel:
                excel.Quit()
            pythoncom.CoUninitialize()

    def extract_txt(self) -> Tuple[DocumentMetadata, List[PageEntry]]:
        """Extract metadata and page entries from text file."""
        logger.info(f"extract txt")
        try:
            with open(self.txt_path, 'r', encoding='utf-16le') as f:
                lines = f.readlines()

            roll = ""
            date = ""
            user = ""
            entries = []
            
            # Extract metadata from header
            for line in lines[:3]:  # First 3 lines should contain metadata
                if "Rollennummer=" in line:
                    roll = line.split("=")[1].strip()
                elif "Datum/Zeit=" in line:
                    date = line.split("=")[1].strip()
                elif "Benutzer=" in line:
                    user = line.split("=")[1].strip()
            
            if not all([roll, date, user]):
                raise ValueError("Missing required metadata in text file")
                
            metadata = DocumentMetadata(roll=roll, date=date, user=user)
            
            # Process page entries
            for line in lines[3:]:
                if not line.strip() or not re.match(r'^\d+\.pdf;', line):
                    continue
                    
                parts = line.strip().split(";")
                if len(parts) < 2:
                    logger.warning(f"Skipping invalid line: {line.strip()}")
                    continue
                    
                barcode = parts[0].split(".")[0]
                blip = parts[1]
                entries.append(PageEntry(barcode=barcode, blip=blip))
            
            return metadata, entries
            
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            raise

    def process_blips(self, entries: List[PageEntry]) -> List[PageEntry]:
        """Process blips to create continuous page numbering."""
        logger.info("processing blips")
        processed_entries = []
        total_pages = 0
        
        # Use defaultdict to avoid explicit check
        barcode_groups = defaultdict(list)
        for entry in entries:
            barcode_groups[entry.barcode].append(entry)
        
        # Process each document
        for doc_entries in barcode_groups.values():
            first_entry = doc_entries[0]
            try:
                doc_num = int(first_entry.blip.split('-')[1])
                new_entry = PageEntry(
                    barcode=first_entry.barcode,
                    blip=f"0-{doc_num}-{total_pages + 1}",
                    com_id=first_entry.com_id
                )
                processed_entries.append(new_entry)
                total_pages += len(doc_entries)
                
            except (IndexError, ValueError) as e:
                logger.error(f"Error processing blip for barcode {first_entry.barcode}: {e}")
                continue
        
        return processed_entries

    def format_output_data(self, entry: PageEntry, roll: str) -> Tuple[str, str, str]:
        """Format output data for Excel file."""
        #logger.info(f"formatting output")
        try:
            # Format blip
            blip_parts = entry.blip.split('-')
            if len(blip_parts) != 3:
                raise ValueError(f"Invalid blip format: {entry.blip}")
                
            blip_formatted1 = f"{int(blip_parts[0])}.{int(blip_parts[1]):04}.{int(blip_parts[2]):05}"
            #blip_formatted2 = f"{int(blip_parts[1]):04}.{int(blip_parts[2]):05}"
            roll_blip = f"{roll}-{blip_formatted1}"
            #roll_blip = f"{blip_formatted2}"
            
            # Return formatted data as tuple
            return (entry.barcode, entry.com_id or "", roll_blip)
            
        except Exception as e:
            logger.error(f"Error formatting output data for entry {entry}: {e}")
            raise

    def process_files(self, barcode_mapping: Dict[str, str]) -> None:
        """Main processing function."""
        logger.info("main")
        excel = None
        try:
            # Initialize COM for this thread
            pythoncom.CoInitialize()
            
            # Extract data from text file only
            metadata, entries = self.extract_txt()
            
            # Process entries more efficiently using passed barcode_mapping
            entries = [
                PageEntry(barcode=entry.barcode, 
                         blip=entry.blip, 
                         com_id=barcode_mapping.get(entry.barcode))
                for entry in entries
            ]
            
            processed_entries = self.process_blips(entries)
            
            # Generate output data more efficiently
            output_data = [
                self.format_output_data(entry, metadata.roll)
                for entry in processed_entries
                if entry.com_id
            ]
            
            # Batch Excel operations
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            
            wb = excel.Workbooks.Add()
            sheet = wb.Sheets(1)
            
            # Set all number formats at once
            sheet.Range(f"A1:C{len(output_data) + 1}").NumberFormat = "@"
            
            # Write headers
            header_range = sheet.Range("A1:C1")
            header_range.Value = ["Barcode", "Com ID", "Roll-Blip"]
            
            # Format header all at once
            header_range.Font.Name = "RR Pioneer"
            header_range.Font.Bold = True
            header_range.Font.Color = 16777215
            header_range.Interior.Color = RGB(16, 6, 159)
            header_range.HorizontalAlignment = -4108
            header_range.VerticalAlignment = -4108
            
            # Write all data at once
            if output_data:
                data_range = sheet.Range(f"A2:C{len(output_data) + 1}")
                data_range.Value = output_data
                
                # Format data range all at once
                data_range.Font.Name = "RR Pioneer"
                data_range.HorizontalAlignment = -4152
            
            # Set column widths
            sheet.Range("A:A").ColumnWidth = 25
            sheet.Range("B:B").ColumnWidth = 15
            sheet.Range("C:C").ColumnWidth = 30
            
            # Set header row height
            sheet.Rows(1).RowHeight = 30
            
            filepath = Path(r"C:\Users\user1\Desktop\Ali\RRD-017-2024\export")
            output_path = filepath / f"{metadata.roll}.xlsx"
            
            wb.SaveAs(str(output_path), FileFormat=51)
            wb.Close(True)
            
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            raise
        finally:
            if excel:
                excel.Quit()
            pythoncom.CoUninitialize()

def process_file(file_path: str, barcode_mapping: Dict[str, str]) -> None:
    """Process a single file using the pre-loaded barcode mapping."""
    try:
        processor = FileProcessor(file_path, "")  # Empty string as xlsx_path is no longer needed
        processor.process_files(barcode_mapping)
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

def main():
    try:
        folder = r"C:\Users\user1\Desktop\Ali\RRD-017-2024\filmlist"
        com_list = r"C:\Users\user1\Desktop\Ali\RRD-017-2024\RRD017-2024_Comlist - FAIR.xls"
        
        # track execution time
        start_time = time.time()

        # Load com_list once before processing files
        processor = FileProcessor("", com_list)  # Empty string as txt_path
        barcode_mapping = processor.extract_xlsx()

        # Process files in parallel with shared barcode_mapping
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            file_paths = [os.path.join(folder, f) for f in os.listdir(folder)]
            futures = [executor.submit(process_file, fp, barcode_mapping) 
                      for fp in file_paths]
            concurrent.futures.wait(futures)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Execution time: {execution_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Program failed: {e}")
        raise

if __name__ == "__main__":
    main()