import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import win32com.client
import tkinter as tk
from tkinter import filedialog
import concurrent.futures
import pythoncom
import time
from collections import defaultdict
import pandas as pd
import os
from threading import Lock

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

excel_lock = Lock()  # Global lock for Excel operations

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

def read_comlist(xlsx_path: Path) -> Dict[str, str]:
    """Read comlist Excel file and return the mapping using pandas."""
    logger.info(f"Reading comlist file: {xlsx_path}")
    try:
        # Using pandas for reading Excel is more efficient and thread-safe
        df = pd.read_excel(xlsx_path)
        
        # Extract the first two columns
        if len(df.columns) < 2:
            raise ValueError(f"Comlist file does not have enough columns: {xlsx_path}")
        
        # Create mapping, assuming first two columns are barcode and com_id
        col1, col2 = df.columns[0], df.columns[1]
        mapping = {
            str(row[col1]).strip().split('.')[0]: str(row[col2]).strip()
            for _, row in df.iterrows()
            if not pd.isna(row[col1]) and not pd.isna(row[col2])
        }
        
        return mapping
        
    except Exception as e:
        logger.error(f"Error reading Excel file with pandas: {e}")
        # Fallback to win32com method if pandas fails
        return read_comlist_legacy(xlsx_path)

def read_comlist_legacy(xlsx_path: Path) -> Dict[str, str]:
    """Legacy method to read comlist using win32com as fallback."""
    logger.info(f"Using legacy method to read comlist file: {xlsx_path}")
    excel = None
    try:
        with excel_lock:  # Use lock for thread safety
            pythoncom.CoInitialize()
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            excel.Visible = False
            
            wb = excel.Workbooks.Open(str(xlsx_path))
            sheet = wb.Sheets(1)
            
            # Read all values at once into an array
            data_range = sheet.UsedRange
            values = data_range.Value
            
            # Process values in memory
            mapping = {
                str(row[0]).strip().split('.')[0]: str(row[1]).strip()
                for row in values
                if row[0] and row[1]
            }
            
            wb.Close(False)
            return mapping
        
    except Exception as e:
        logger.error(f"Error in legacy Excel processing: {e}")
        raise
    finally:
        if excel:
            excel.Quit()
        pythoncom.CoUninitialize()

class FileProcessor:
    def __init__(self, txt_path: str, barcode_mapping: Dict[str, str], output_dir: Path):
        self.txt_path = Path(txt_path)
        self.barcode_mapping = barcode_mapping
        self.output_dir = output_dir
        self.validate_files()
        # Add output data storage
        self.dat_entries = []
        self.excel_entries = []

    def validate_files(self) -> None:
        if not self.txt_path.exists():
            raise FileNotFoundError(f"Text file not found: {self.txt_path}")
        if self.txt_path.suffix.lower() != '.txt':
            raise ValueError(f"Expected .txt file, got: {self.txt_path}")

    def extract_txt(self) -> Tuple[DocumentMetadata, List[PageEntry]]:
        """Extract metadata and page entries from text file."""
        try:
            encoding = 'utf-16le'  # Primary encoding
            try:
                with open(self.txt_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
            except UnicodeError:
                # Fallback to UTF-8 if UTF-16LE fails
                encoding = 'utf-8'
                with open(self.txt_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                    
            logger.info(f"Read file {self.txt_path} with encoding {encoding}")

            metadata = None
            entries = []
            roll = date = user = ""
            
            # Extract metadata from header
            for line in lines[:10]:  # Check more lines for metadata
                if "Rollennummer=" in line:
                    roll = line.split("=")[1].strip()
                elif "Datum/Zeit=" in line:
                    date = line.split("=")[1].strip()
                elif "Benutzer=" in line:
                    user = line.split("=")[1].strip()
            
            if not all([roll, date, user]):
                raise ValueError("Missing required metadata in text file")
                
            metadata = DocumentMetadata(roll=roll, date=date, user=user)
            
            # Compile regex for better performance
            pdf_pattern = re.compile(r'^\d+\.pdf;')
            
            # Process page entries
            for line in lines[3:]:
                if not line.strip() or not pdf_pattern.match(line):
                    continue
                    
                parts = line.strip().split(";")
                if len(parts) < 2:
                    continue
                    
                barcode = parts[0].split(".")[0]
                blip = parts[1]
                com_id = self.barcode_mapping.get(barcode)
                entries.append(PageEntry(barcode=barcode, blip=blip, com_id=com_id))
            
            return metadata, entries
            
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            raise

    def process_blips(self, entries: List[PageEntry]) -> List[PageEntry]:
        """Process blips to create continuous page numbering."""
        processed_entries = []
        total_pages = 0
        
        barcode_groups = defaultdict(list)
        for entry in entries:
            barcode_groups[entry.barcode].append(entry)
        
        for doc_entries in barcode_groups.values():
            first_entry = doc_entries[0]
            try:
                blip_parts = first_entry.blip.split('-')
                if len(blip_parts) < 2:
                    logger.warning(f"Invalid blip format for barcode {first_entry.barcode}: {first_entry.blip}")
                    continue
                    
                doc_num = int(blip_parts[1])
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

    def process_file(self) -> Tuple[List[str], List[List]]:
        """Process a single file and return data for combined outputs."""
        try:
            metadata, entries = self.extract_txt()
            processed_entries = self.process_blips(entries)
            
            # Filter entries with com_id for efficiency
            valid_entries = [entry for entry in processed_entries if entry.com_id]
            
            if not valid_entries:
                logger.warning(f"No valid entries found with COM IDs in {self.txt_path}")
                return [], []
                
            # Prepare data for combined files
            dat_lines = []
            excel_rows = []
            
            for entry in valid_entries:
                blip_parts = entry.blip.split('-')
                blip_formatted = f"{int(blip_parts[0])}.{int(blip_parts[1]):04}.{int(blip_parts[2]):05}"
                roll_blip = f"{metadata.roll}-{blip_formatted}"
                
                # DAT file line
                dat_lines.append(f"{entry.com_id:<13}{entry.barcode:<48}{roll_blip}")
                
                # Excel row
                excel_rows.append([entry.barcode, entry.com_id, roll_blip])
            
            return dat_lines, excel_rows
            
        except Exception as e:
            logger.error(f"Error processing file {self.txt_path}: {e}")
            raise

def process_file_wrapper(args):
    """Wrapper function for multiprocessing to handle multiple arguments."""
    txt_file, barcode_mapping, output_dir = args
    try:
        processor = FileProcessor(txt_file, barcode_mapping, output_dir)
        return processor.process_file()
    except Exception as e:
        logger.error(f"Error processing {txt_file}: {e}")
        return [], []

def create_combined_excel(output_dir: Path, all_excel_rows: List[List]) -> None:
    """Create a single combined Excel file."""
    try:
        # Create DataFrame
        df = pd.DataFrame(all_excel_rows, columns=["Barcode", "Bildnummer", "Blipnummer"])
        
        # Create Excel file with pandas
        output_path = output_dir / "scan.xlsx"
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Format headers
            header_format = workbook.add_format({
                'bold': True,
                'font_name': 'Arial',
                'font_color': 'white',
                'bg_color': '#10069F',
                'align': 'center'
            })
            
            # Format data cells
            data_format = workbook.add_format({
                'font_name': 'Arial',
                'align': 'left'
            })
            
            # Apply formats
            for col_num, _ in enumerate(df.columns):
                worksheet.write(0, col_num, df.columns[col_num], header_format)
                worksheet.set_column(col_num, col_num, [25, 15, 30][col_num], data_format)
        
        logger.info(f"Created combined Excel file: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating combined Excel file: {e}")
        raise

def main():
    try:
        # Create root window and hide it
        root = tk.Tk()
        root.withdraw()

        # Ask for input folder
        input_folder = filedialog.askdirectory(title="Select Input Folder")
        if not input_folder:
            logger.error("No input folder selected")
            return

        input_folder = Path(input_folder)
        output_dir = input_folder / "export"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find comlist file
        comlist_file = None
        for pattern in ["*Comlist*", "*comlist*"]:  # Case-insensitive search
            for ext in ['.xls', '.xlsx']:
                files = list(input_folder.glob(f"{pattern}{ext}"))
                if files:
                    comlist_file = files[0]
                    break
            if comlist_file:
                break

        if not comlist_file:
            logger.error("Could not find Comlist file")
            return

        # Read comlist once
        barcode_mapping = read_comlist(comlist_file)
        logger.info(f"Loaded {len(barcode_mapping)} barcode mappings")

        # Get list of text files to process
        txt_files = list(input_folder.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} text files to process")

        if not txt_files:
            logger.warning("No text files found to process")
            return

        # Prepare arguments for multiprocessing
        process_args = [(str(txt_file), barcode_mapping, output_dir) for txt_file in txt_files]

        # Process files in parallel and collect results
        start_time = time.time()
        max_workers = min(os.cpu_count() or 4, 8)
        
        all_dat_lines = []
        all_excel_rows = []
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_file_wrapper, process_args))
            
            # Combine results
            for dat_lines, excel_rows in results:
                all_dat_lines.extend(dat_lines)
                all_excel_rows.extend(excel_rows)
        
        # Create combined DAT file
        if all_dat_lines:
            dat_path = output_dir / "scan.dat"
            with open(dat_path, 'w', encoding="utf-8") as f:
                f.write("\n".join(all_dat_lines))
            logger.info(f"Created combined DAT file: {dat_path}")
        
        # Create combined Excel file
        if all_excel_rows:
            create_combined_excel(output_dir, all_excel_rows)
        
        execution_time = time.time() - start_time
        logger.info(f"Processing complete! Created combined output files in {execution_time:.2f} seconds")

    except Exception as e:
        logger.error(f"Program failed: {e}")
        raise

if __name__ == "__main__":
    main()