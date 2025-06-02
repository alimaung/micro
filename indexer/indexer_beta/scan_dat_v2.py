import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import xlwings as xw
import tkinter as tk
from tkinter import filedialog
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    """Read comlist Excel file once and return the mapping."""
    logger.info(f"Reading comlist file: {xlsx_path}")
    try:
        wb = xw.Book(str(xlsx_path))
        sheet = wb.sheets[0]
        wb.Visible = False
        
        mapping = {}
        last_row = sheet.range("A" + str(sheet.cells.last_cell.row)).end('up').row
        
        for row in range(1, last_row + 1):
            barcode = str(sheet.range(f"A{row}").value).strip()
            com_id = str(sheet.range(f"B{row}").value).strip()
            
            if not barcode or not com_id:
                logger.warning(f"Skipping row {row}: Missing barcode or com_id")
                continue
                
            mapping[barcode] = com_id
        
        wb.close()
        return mapping
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {e}")
        raise

class FileProcessor:
    def __init__(self, txt_path: str, barcode_mapping: Dict[str, str], output_dir: Path):
        self.txt_path = Path(txt_path)
        self.barcode_mapping = barcode_mapping
        self.output_dir = output_dir
        self.validate_files()

    def validate_files(self) -> None:
        """Validate that input files exist and have correct extensions."""
        if not self.txt_path.exists():
            raise FileNotFoundError(f"Text file not found: {self.txt_path}")
        
        if self.txt_path.suffix.lower() != '.txt':
            raise ValueError(f"Expected .txt file, got: {self.txt_path}")

    def extract_txt(self) -> Tuple[DocumentMetadata, List[PageEntry]]:
        """Extract metadata and page entries from text file."""
        try:
            with open(self.txt_path, 'r', encoding='utf-16le') as f:
                lines = f.readlines()

            metadata = None
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
        processed_entries = []
        total_pages = 0
        
        # Group by barcode
        barcode_groups = {}
        for entry in entries:
            if entry.barcode not in barcode_groups:
                barcode_groups[entry.barcode] = []
            barcode_groups[entry.barcode].append(entry)
        
        # Process each document
        for barcode, doc_entries in barcode_groups.items():
            first_entry = doc_entries[0]
            try:
                doc_num = int(first_entry.blip.split('-')[1])
                new_blip = f"0-{doc_num}-{total_pages + 1}"
                
                new_entry = PageEntry(
                    barcode=first_entry.barcode,
                    blip=new_blip,
                    com_id=first_entry.com_id
                )
                processed_entries.append(new_entry)
                total_pages += len(doc_entries)
                
            except (IndexError, ValueError) as e:
                logger.error(f"Error processing blip for barcode {barcode}: {e}")
                continue
        
        return processed_entries

    def format_output_line(self, entry: PageEntry, roll: str) -> str:
        """Format a single output line for scan.dat."""
        try:
            # Format blip
            blip_parts = entry.blip.split('-')
            if len(blip_parts) != 3:
                raise ValueError(f"Invalid blip format: {entry.blip}")
                
            blip_formatted = f"{int(blip_parts[0])}.{int(blip_parts[1]):04}.{int(blip_parts[2]):05}"
            roll_blip = f"{roll}-{blip_formatted}"
            
            # Format full line
            return f"{entry.barcode:<21}{entry.com_id or '':<40}{roll_blip}"
            
        except Exception as e:
            logger.error(f"Error formatting output line for entry {entry}: {e}")
            raise

    def process_file(self) -> None:
        """Main processing function."""
        try:
            # Extract data from text file
            metadata, entries = self.extract_txt()
            
            # Add com_ids to entries using the pre-loaded mapping
            for entry in entries:
                entry.com_id = self.barcode_mapping.get(entry.barcode)
                if not entry.com_id:
                    logger.warning(f"No com_id found for barcode: {entry.barcode}")
            
            # Process blips for continuous numbering
            processed_entries = self.process_blips(entries)
            
            # Generate output
            output_lines = []
            for entry in processed_entries:
                if not entry.com_id:
                    logger.warning(f"Skipping entry with missing com_id: {entry.barcode}")
                    continue
                output_lines.append(self.format_output_line(entry, metadata.roll))
            
            # Create output filename based on input filename
            output_filename = f"{self.txt_path.stem}.dat"
            output_path = self.output_dir / output_filename
            
            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write output file
            output_path.write_text("\n".join(output_lines), encoding="utf-8")
            logger.info(f"Successfully created {output_path}")
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise

def process_folder(input_folder: Path, barcode_mapping: Dict[str, str], output_dir: Path) -> None:
    """Process all text files in the input folder."""
    for txt_file in input_folder.glob("*.txt"):
        try:
            logger.info(f"Processing {txt_file}")
            processor = FileProcessor(str(txt_file), barcode_mapping, output_dir)
            processor.process_file()
        except Exception as e:
            logger.error(f"Failed to process {txt_file}: {e}")

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

        # Convert to Path object
        input_folder = Path(input_folder)
        
        # Create export directory next to input folder
        output_dir = input_folder.parent / "export"
        
        # Look for the Excel file in the parent directory
        xlsx_path = next(input_folder.parent.glob("*Comlist*.xls"), None)
        if not xlsx_path:
            logger.error("Could not find Comlist Excel file")
            return

        # Read the comlist Excel file once
        barcode_mapping = read_comlist(xlsx_path)
        
        # Process all files in the folder using the same mapping
        process_folder(input_folder, barcode_mapping, output_dir)
        
        logger.info("Processing complete!")
        
    except Exception as e:
        logger.error(f"Program failed: {e}")
        raise

if __name__ == "__main__":
    main()