import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import xlwings as xw

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

class FileProcessor:
    def __init__(self, txt_path: str, xlsx_path: str):
        self.txt_path = Path(txt_path)
        self.xlsx_path = Path(xlsx_path)
        self.validate_files()

    def validate_files(self) -> None:
        """Validate that input files exist and have correct extensions."""
        if not self.txt_path.exists():
            raise FileNotFoundError(f"Text file not found: {self.txt_path}")
        if not self.xlsx_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.xlsx_path}")
        
        if self.txt_path.suffix.lower() != '.txt':
            raise ValueError(f"Expected .txt file, got: {self.txt_path}")
        if self.xlsx_path.suffix.lower() != '.xlsx':
            raise ValueError(f"Expected .xlsx file, got: {self.xlsx_path}")

    def extract_xlsx(self) -> Dict[str, str]:
        """Extract barcode to com_id mapping from Excel file."""
        try:
            wb = xw.Book(str(self.xlsx_path))
            sheet = wb.sheets[0]
            
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

    def process_files(self) -> None:
        """Main processing function."""
        try:
            # Extract data from both files
            barcode_mapping = self.extract_xlsx()
            metadata, entries = self.extract_txt()
            
            # Add com_ids to entries
            for entry in entries:
                entry.com_id = barcode_mapping.get(entry.barcode)
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
            
            # Write output file
            output_path = Path("scan.dat")
            output_path.write_text("\n".join(output_lines), encoding="utf-8")
            logger.info(f"Successfully created {output_path}")
            
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            raise

def main():
    try:
        processor = FileProcessor("430179.txt", "RRD095-2024_ComList.xlsx")
        processor.process_files()
    except Exception as e:
        logger.error(f"Program failed: {e}")
        raise

if __name__ == "__main__":
    main()