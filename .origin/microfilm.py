# Import necessary libraries
import os, re, json, sys, sqlite3, xlwings as xw, copy, shutil, math, subprocess
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from operator import itemgetter
from itertools import groupby
from tkinter import filedialog
from datetime import datetime
from typing import Dict, List, Tuple, Set, Any, Optional
from io import BytesIO
from logger import get_logger, LogLevel, FilmLogger
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from tqdm import tqdm

logger = get_logger(name="FilmProcessor", log_level=LogLevel.DEBUG.value)

# Define constants
OVERSIZE_THRESHOLD_WIDTH = 842
OVERSIZE_THRESHOLD_HEIGHT = 1191
CAPACITY_16MM = 2900
CAPACITY_35MM = 690
TEMP_ROLL_PADDING_16MM = 150
TEMP_ROLL_PADDING_35MM = 150
TEMP_ROLL_MIN_USABLE_PAGES = 100
DB_FILE = "film_allocation.sqlite3"


# --------------------------------  PROJECT INITIALIZATION  --------------------------------
"""
This section extracts and stores project metadata from folder names and paths:
1. path: Full path to the project folder
2. folderName: Name of the current folder
3. parentFolderName: Name of the parent folder
4. archiveId: Archive ID extracted from parent folder name (format: RRDxxx-xxxx)
5. location: Location code extracted from parent folder name (OU or DW)
6. doc_type: Document type extracted from the last part of parent folder name
7. oversized: Boolean flag indicating if any document contains oversized pages
8. totalPages: Total number of pages across all documents
9. film_allocation: Detailed information about film requirements

The project_info dictionary serves as the central repository for project metadata
and is updated throughout the processing pipeline.

Structure of project_info dictionary:
{
    "parent_folder_name": {
        "path": str,                # Full path to the folder
        "folderName": str,          # Name of the folder
        "parentFolderName": str,    # Name of the parent folder
        "parentFolderPath": str,    # Store the parent folder path
        "archiveId": str,           # Archive ID (e.g., "RRD018-2024")
        "location": str,            # Location code (e.g., "DW" or "OU")
        "doc_type": str,            # Document type (e.g., "FAIR")
        "oversized": bool,          # Whether project contains oversized pages
        "totalPages": int,          # Total number of pages across all documents
        "film_allocation": {        # Film allocation information
            "documentInfo": {
                "totalReferences": int,  # Total reference sheets added
                "totalPages16": int,     # Total pages for 16mm film
                "totalPages35": int,     # Total pages for 35mm film
                "location": str          # Project location code
            },
            "filmAllocation": {
                "allocation16": int,     # Total pages allocated to 16mm
                "rolls16": int,          # Number of 16mm rolls needed
                "allocation35": int,     # Total pages allocated to 35mm
                "rolls35": int           # Number of 35mm rolls needed
            }
        }
    }
}
"""

def initialize_project(input_folder_path: str, comlist_path: Optional[str] = None) -> Tuple[Dict[str, Any], Path, str, str, str]:
    """
    Initialize project metadata from folder paths and names.
    
    Args:
        input_folder_path: Path to the folder containing PDF documents
        
    Returns:
        tuple: (project_info, folder_path, folder_name, parent_folder_name)
    """

    # Use the existing logger instead of creating a new one
    logger.info(f"Initializing project from: {input_folder_path}")
    
    
    logger.section("INITIALIZING PROJECT")
    
    # Get basic information folder name
    try:
        folder_path = Path(input_folder_path)
        folder_name = folder_path.name
        parent_folder_path = folder_path.parent
        parent_folder_name = folder_path.parent.name
        
        logger.debug("Parsed init path:", folder_path=str(folder_path))
        logger.debug("Parsed folder name:", folder_name=folder_name)
        logger.debug("Parsed parent folder path:", parent_folder_path=str(parent_folder_path))
        logger.debug("Parsed parent folder name:", parent_folder_name=parent_folder_name)
        
        # Update logger's parent folder to save logs in the parent directory
        logger.parent_folder = str(parent_folder_path)
        logger.save_log_file(archive_id=parent_folder_name)
        logger.info(f"Logs will be saved to: {os.path.join(str(parent_folder_path), '.logs')}")
        
        # Ensure all subsequent log messages are captured
        logger.info("Logging system initialized")
        
        project_info: Dict[str, Any] = {}

        # Store basic folder information
        project_info[parent_folder_name] = {
            "path": str(folder_path),
            "folderName": folder_name,
            "parentFolderName": parent_folder_name,
            "parentFolderPath": str(parent_folder_path),  # Store the parent folder path
            "oversized": False,  # Initialize oversized flag to False
        }

        logger.project(f"Created project entry for {parent_folder_name}")
    except Exception as e:
        logger.critical(f"Error initializing folder paths: {str(e)}")
        raise
        
    # Extract metadata from folder name
    try:
        # Extract archive ID (format: RRDxxx-xxxx)
        order_match = re.search(r'(RRD\d{3}-\d{4})', parent_folder_name)
        archive_id = order_match.group(1) if order_match else "Unknown"

        # Extract location from project name (OU|DW)
        location_match = re.search(r'_(OU|DW)_', parent_folder_name)
        location = location_match.group(1) if location_match else "Unknown"

        # Extract type from project name (after the last underscore)
        doc_type_match = re.search(r'_([^_]+)$', parent_folder_name)
        doc_type = doc_type_match.group(1) if doc_type_match else "Unknown"

        logger.project(f"Project metadata extracted", 
                    archive_id=archive_id,
                    location=location,
                    doc_type=doc_type)

        # Update project info with extracted metadata
        project_info[parent_folder_name].update({
            "archiveId": archive_id,
            "location": location,
            "doc_type": doc_type,
        })
        
        # Update log file with archive_id
        if archive_id != "Unknown":
            logger.save_log_file(archive_id=archive_id)
        else:
            logger.warning("No archive ID found in folder name")
            logger.save_log_file()
                        
        logger.success(f"Successfully initialized project {parent_folder_name}")                       
    except Exception as e:
        logger.error(f"Error parsing project information: {str(e)}")

    # Find comlist excel file in folder
    try:
        dir_contents = os.listdir(parent_folder_path)
        
        # Look for any Excel file in the directory
        excel_files = [f for f in dir_contents if f.lower().endswith(('.xlsx', '.xls'))]
        
        if excel_files:
            comlist_path = os.path.join(parent_folder_path, excel_files[0])
            logger.info(f"Found Excel file: {excel_files[0]}")
            
            # Save the comlist path in project info
            project_info[parent_folder_name]["comlist_path"] = comlist_path
        else:
            logger.warning(f"No comlist Excel file found in the folder: {excel_files}")
            project_info[parent_folder_name]["comlist_path"] = None
    except Exception as e:
        logger.error(f"Error finding comlist Excel file: {str(e)}")
        project_info[parent_folder_name]["comlist_path"] = None

            
    return project_info, folder_path, folder_name, parent_folder_name, comlist_path

# --------------------------------  DOCUMENT PREPROCESSING --------------------------------
"""
This section processes each PDF document to extract page information and identify oversized pages:
1. path: Full path to the PDF file
2. pages: Total number of pages in the document
3. oversized: Boolean flag indicating if document contains any oversized pages
4. totalOversized: Count of oversized pages in the document
5. dimensions: List of tuples containing dimensions, page indices, and percentage over threshold of oversized pages
6. ranges: List of page ranges (start, end) for consecutive oversized pages
7. com_id: The COM ID associated with the document (from comlist Excel file)

An oversized page is defined as exceeding:
- Width > 842 points AND Height > 1191 points (A3 size)
- This applies in both portrait and landscape orientations

The ranges are calculated by:
1. Identifying consecutive page numbers of oversized pages
2. Grouping them into ranges (start, end) for more efficient processing
3. These ranges will later determine where reference sheets need to be inserted

Structure of document_pages dictionary:
document_pages = {
    document_name : {  # Document ID/name as the dictionary key
        path: str,     # Full path to the PDF file
        pages: int,    # Total number of pages in the document
        oversized: bool,  # Flag indicating if document contains any oversized pages
        totalOversized: int,  # Count of oversized pages in the document
        dimensions: List[Tuple[float, float, int, float]],  # (width, height, page_index, percent_over)
        ranges: List[Tuple[int, int]],  # List of page ranges (start_page, end_page)
        com_id: int    # COM ID from comlist Excel file
    }
}
"""

def identify_oversized_pages(folder_path: Path, project_info: Dict[str, Any], parent_folder_name: str) -> Tuple[Dict[str, Any], bool, int, int]:
    """
    Process all PDF documents, extract page count information, and identify oversized pages.
    This function combines the functionality of process_documents and identify_oversized_pages.
    
    Args:
        folder_path: Path object pointing to folder containing PDFs
        project_info: Dictionary containing project metadata
        parent_folder_name: Name of the parent folder
        
    Returns:
        tuple: (document_pages, has_oversized, total_oversized, documents_with_oversized)
            - document_pages: Dictionary containing document information
            - has_oversized: Boolean indicating if any document has oversized pages
            - total_oversized: Total count of oversized pages across all documents
            - documents_with_oversized: Count of documents that contain oversized pages
    """
    
    logger.section("PROCESSING DOCUMENTS AND IDENTIFYING OVERSIZED PAGES")
    
    
    # Initialize variables
    document_pages = {}
    total_page_count = 0
    has_oversized = False
    total_oversized = 0
    documents_with_oversized = 0
    
    # Process files in the folder
    sorted_documents = sorted(os.listdir(folder_path), key=lambda x: (x.lower()))
    pdf_count = sum(1 for doc in sorted_documents if doc.lower().endswith('.pdf'))
    
    # Initialize progress tracking
    logger.start_progress(pdf_count, prefix="Processing PDFs:", suffix="Complete")
    
    i = 0  # Counter for progress tracking

    # Process each document
    for document in sorted_documents:
        if document.lower().endswith('.pdf'):
            doc_path = folder_path / document
            try:
                # Extract document ID from file name or use the file name itself
                doc_id_match = re.search(r'^\d+', document)
                doc_id = doc_id_match.group(0) if doc_id_match else document.replace('.pdf', '')
                
                # Open the PDF file
                pdf_reader = PdfReader(str(doc_path))
                pages_count = len(pdf_reader.pages)
                total_page_count += pages_count
                
                # Initialize document structure
                document_pages[doc_id] = {
                    "path": str(doc_path),
                    "pages": pages_count,
                    "oversized": False,
                    "totalOversized": 0,
                }
                
                #logger.document(f"Processing document", doc_name=doc_id)
                
                # Check for oversized pages
                dimensions: List[Tuple[float, float, int, float]] = []  # (width, height, page_index, percent_over)
                paper_sizes: List[Tuple[str, int]] = []  # List for oversized pages only
                doc_oversized = 0
                
                # Check each page for oversized dimensions
                for index, page in enumerate(pdf_reader.pages):
                    # Get page dimensions from mediabox
                    mediabox = page.mediabox
                    width, height = float(mediabox[2]), float(mediabox[3])
                                    
                    # Check if page is oversized
                    is_oversized = ((width > OVERSIZE_THRESHOLD_WIDTH and height > OVERSIZE_THRESHOLD_HEIGHT) or
                                    (width > OVERSIZE_THRESHOLD_HEIGHT and height > OVERSIZE_THRESHOLD_WIDTH))
                    
                    # Mark oversized pages and collect their dimensions
                    if is_oversized:
                        # Calculate percentage over threshold
                        width_percent = (width / OVERSIZE_THRESHOLD_WIDTH - 1) * 100
                        height_percent = (height / OVERSIZE_THRESHOLD_HEIGHT - 1) * 100
                        max_percent = max(width_percent, height_percent)
                        
                        logger.debug(f"Found oversized page",
                                   doc_name=doc_id, 
                                   page=index+1, 
                                   width=width, 
                                   height=height,
                                   percent_over=max_percent)
                        
                        document_pages[doc_id]["oversized"] = True
                        dimensions.append((width, height, index, max_percent))
                        doc_oversized += 1
                        total_oversized += 1
                        has_oversized = True
                        project_info[parent_folder_name]["oversized"] = True
                    
                # Store oversized page information
                document_pages[doc_id]["totalOversized"] = doc_oversized
                document_pages[doc_id]["dimensions"] = dimensions
                
                # Only add paper_sizes if there are oversized pages
                if paper_sizes:
                    document_pages[doc_id]["paper_sizes"] = paper_sizes
                
                if doc_oversized > 0:
                    documents_with_oversized += 1
                    logger.document(f"Document has oversized pages", 
                                  doc_name=doc_id, 
                                  oversized_count=doc_oversized)
            
                    # Create page ranges for oversized pages
                    page_info = document_pages[doc_id]["dimensions"] 
                    page_indices = [page_idx for _, _, page_idx, _ in page_info]  # Extract page indices
                    page_numbers = [idx + 1 for idx in page_indices]  # Convert to 1-based page numbers
            
                    # Group consecutive page numbers into ranges
                    ranges: List[Tuple[int, int]] = []
                    for _, g in groupby(enumerate(sorted(page_numbers)), lambda x: x[0] - x[1]):
                        group = list(map(itemgetter(1), g))
                        if len(group) > 1:
                            ranges.append((group[0], group[-1]))
                        else:
                            ranges.append((group[0], group[0]))

                    # Set the ranges once after the loop is complete
                    document_pages[doc_id]["ranges"] = ranges
                    
                    # Create human-readable page ranges for oversized pages
                    readable_pages = []
                    current_count = 1
                    for start, end in ranges:
                        range_size = end - start + 1
                        if range_size == 1:
                            # Single page format: "X von Y"
                            readable_pages.append(f"{current_count} von {doc_oversized}")
                        else:
                            # Range format: "X bis Y von Z"
                            readable_pages.append(f"{current_count} bis {current_count + range_size - 1} von {doc_oversized}")
                        current_count += range_size
                    
                    # Store the human-readable page ranges
                    document_pages[doc_id]["readable_pages"] = readable_pages
                    
                    # Calculate adjusted ranges for oversized pages
                    adjusted_ranges = []
                    offset = 0  # Track how many reference pages we've added so far
                    
                    # Sort ranges by their original position to maintain order
                    sorted_ranges = sorted(ranges, key=lambda x: x[0])
                    
                    for start, end in sorted_ranges:
                        # The reference sheet is inserted at the adjusted position
                        adjusted_start = start + offset
                        adjusted_end = end + offset
                        adjusted_ranges.append((adjusted_start, adjusted_end))
                        offset += 1  # Increment offset for each reference sheet added
                    
                    # Store the adjusted ranges
                    document_pages[doc_id]["adjusted_ranges"] = adjusted_ranges
                    
                    logger.debug(f"Created ranges for oversized pages", 
                               doc_name=doc_id, 
                               ranges=ranges,
                               readable_pages=readable_pages)
                
                # Update progress
                i += 1
                logger.update_progress(i)
                
            except Exception as e:
                logger.error(f"Error processing {document}: {e}")
                raise
    
    # Finish progress tracking
    logger.finish_progress()
    
    # Update project info with total pages
    project_info[parent_folder_name]["totalPages"] = total_page_count
    
    logger.success(f"Processed {len(document_pages)} documents with {total_page_count} total pages")
    logger.success(f"Identified {total_oversized} oversized pages in {documents_with_oversized} documents")
    logger.debug(f"Oversized detection complete: {documents_with_oversized} documents with oversized pages")
    logger.debug(f"Project oversized flag is now: {project_info[parent_folder_name]['oversized']}")
    
    return document_pages, has_oversized, total_oversized, documents_with_oversized

def calculate_references(document_pages: Dict[str, Any]) -> int:
    """
    Calculate reference page positions for documents with oversized pages.
    
    Args:
        document_pages: Dictionary containing document information
        
    Returns:
        int: Total number of reference sheets added
    """
    
    logger.section("CALCULATING REFERENCE PAGES")
    
    
    total_reference_count = 0

    for document_name, document_data in document_pages.items():
        # Skip documents with no oversized pages
        if not document_data.get("oversized", False) or not document_data.get("ranges"):
            document_data["references"] = {
                "pages": [],
                "totalReferences": 0
            }
            continue
        
        # Get the ranges of oversized pages
        ranges = document_data["ranges"]
        
        # Calculate reference page positions
        reference_pages: List[int] = []
        offset = 0  # Track how many reference pages we've added so far
        
        for range_start, range_end in ranges:
            # The actual position where we'll insert the reference page
            # is the original range start + the number of references already added
            reference_position = range_start + offset
            reference_pages.append(reference_position)
            offset += 1  # Increment offset for each reference page added
        
        # Store reference page information
        document_data["references"] = {
            "pages": reference_pages,
            "totalReferences": len(reference_pages)
        }
        
        total_reference_count += len(reference_pages)
        
        logger.document(f"Calculated reference pages", 
                    doc_name=document_name, 
                    ref_count=len(reference_pages), 
                    ref_positions=reference_pages)
    
    logger.success(f"Added {total_reference_count} reference pages across all documents")
    return total_reference_count

# --------------------------------  ALLOCATION CALCULATIONS -------------------------------
"""
This section determines how many film rolls are needed by calculating:
1. totalReferences: Number of reference sheets needed (one before each oversized page range)
2. totalPages16: All document pages plus reference sheets for 16mm film
3. totalPages35: Only oversized pages plus reference sheets for 35mm film
4. allocation16/35: Total pages allocated to each film type (same as totalPages16/35)
5. rolls16/35: Number of rolls needed, calculated by dividing total pages by film capacity

Each film type has different capacity:
- 16mm: 2900 pages per roll (used for all pages)
- 35mm: 690 pages per roll (used only for oversized pages)

Film allocation is location-aware, ensuring that:
- Film numbers follow location-specific prefixes (OU: 1, DW: 2, Other: 3)
- 35mm rolls are only reused within the same location
- Each project's location is considered when allocating film numbers

Structure of film_allocation dictionary:
film_allocation = {
    parent_folder_name: {
        "documentInfo": {
            "totalReferences": int,   # Total reference sheets added across all documents
            "totalPages16": int,      # Total number of pages for 16mm film (including references)
            "totalPages35": int,      # Total number of pages for 35mm film (oversized + references)
            "location": str,          # Project location code (e.g., "OU" or "DW")
        },
        "filmAllocation": {
            "allocation16": int,      # Total pages allocated to 16mm film
            "rolls16": int,           # Number of 16mm rolls needed
            "allocation35": int,      # Total pages allocated to 35mm film
            "rolls35": int            # Number of 35mm rolls needed
        }
    }
}
"""

def calculate_film_allocation(parent_folder_name: str, film_allocation: Dict[str, Any], 
                              document_pages: Dict[str, Any], total_page_count: int, 
                              reference_sheet_count: int) -> Dict[str, Any]:
    """
    Calculate film allocation requirements for 16mm and 35mm film.
    
    Args:
        parent_folder_name: Name of the parent folder
        film_allocation: Dictionary to store allocation information
        document_pages: Dictionary containing document information
        total_page_count: Total number of pages across all documents
        reference_sheet_count: Total number of reference sheets added
        
    Returns:
        dict: Updated film_allocation dictionary
    """
    
    logger.section("CALCULATING FILM ALLOCATION")
    

    try:
        # Calculate total oversized pages
        oversized_page_count = sum(document_pages[barcode].get("totalOversized", 0) for barcode in document_pages)
        
        logger.film(f"Calculating film allocation", 
                   total_pages=total_page_count, 
                   total_refs=reference_sheet_count, 
                   total_oversized=oversized_page_count)
    
        # Calculate 16mm allocation (all pages + references)
        pages_16mm = total_page_count + reference_sheet_count
        rolls_16mm = (pages_16mm + CAPACITY_16MM - 1) // CAPACITY_16MM if pages_16mm > 0 else 0
        
        # Calculate 35mm allocation (oversized pages + references)
        pages_35mm = oversized_page_count + reference_sheet_count
        rolls_35mm = (pages_35mm + CAPACITY_35MM - 1) // CAPACITY_35MM if pages_35mm > 0 else 0
        
        logger.film(f"Film requirements calculated", 
                   pages_16mm=pages_16mm, 
                   rolls_16mm=rolls_16mm, 
                   pages_35mm=pages_35mm, 
                   rolls_35mm=rolls_35mm)
        
        # Update film allocation
        film_allocation[parent_folder_name]["documentInfo"]["totalReferences"] = reference_sheet_count
        film_allocation[parent_folder_name]["documentInfo"]["totalPages16"] = pages_16mm
        film_allocation[parent_folder_name]["documentInfo"]["totalPages35"] = pages_35mm
        film_allocation[parent_folder_name]["filmAllocation"]["allocation16"] = pages_16mm
        film_allocation[parent_folder_name]["filmAllocation"]["rolls16"] = rolls_16mm
        film_allocation[parent_folder_name]["filmAllocation"]["allocation35"] = pages_35mm
        film_allocation[parent_folder_name]["filmAllocation"]["rolls35"] = rolls_35mm
        
        logger.success(f"Film allocation requirements calculated successfully")
        
    except Exception as e:
        logger.error(f"Error calculating film allocation: {str(e)}")
    
    return film_allocation

def no_oversizes(document_pages, parent_folder_name, folder_name, project_info=None) -> Dict[str, Any]:
    """
    Allocate documents to 16mm film rolls when there are no oversized pages.
    Documents will NOT be split across rolls unless they are larger than the roll capacity.
    
    Returns:
        dict: Film rolls allocation information
    """
    
    logger.section("16MM FILM ALLOCATION - NO OVERSIZES")
    

    # Extract archive_id from project_info
    archive_id = ""
    for project_key, project_data in project_info.items():
        if project_key == parent_folder_name and "archiveId" in project_data:
            archive_id = project_data["archiveId"]
            break
    
    film_rolls: Dict[str, Any] = {
        "metadata": {
            "archive_id": archive_id,
            "project_name": folder_name,
            "creation_date": datetime.now().isoformat(),
            "version": "1.0"
        },
        "rolls": {},
        "splitDocumentsDetails": {},
        "partialRolls": [],
        "statistics": {
            "total_rolls": 0,
            "total_pages": 0,
            "total_partial_rolls": 0,
            "total_split_documents": 0
        }
    }

    logger.film("Initializing 16mm film allocation without oversized pages")

    # Track which documents are split across rolls
    split_documents: Set[str] = set()
    
    # Sort documents alphabetically
    sorted_documents = sorted(document_pages.keys())
    logger.debug(f"Processing {len(sorted_documents)} documents in alphabetical order")
    
    # Initialize progress tracking
    logger.start_progress(len(sorted_documents), prefix="Allocating documents:", suffix="Complete")
    
    current_roll_id = 1
    
    # Initialize the first roll
    film_rolls["rolls"][str(current_roll_id)] = {
        "pages": CAPACITY_16MM,
        "pagesUsed": 0,
        "pagesRemaining": CAPACITY_16MM,
        "documents": {},
        "hasSplitDocuments": False,
        "isPartial": False,
        "partialRollInfo": None,
        "film_number": None,
        "temp_roll_id": None,
        "status": "active",
        "creation_date": datetime.now().isoformat(),
        "next_document_index": 1  # Track the next document index for this roll
    }
    
    logger.film(f"Created roll {current_roll_id} with capacity {CAPACITY_16MM}")
    
    # Process each document in alphabetical order
    for doc_idx, doc_name in enumerate(sorted_documents):
            
        # Update progress
        logger.update_progress(doc_idx + 1)
        
        doc_data = document_pages[doc_name]
        doc_pages = doc_data["pages"]
        
        #logger.allocation(f"Processing document for allocation", 
        #                doc_name=doc_name, 
        #                pages=doc_pages)
        
        # Check if document exceeds roll capacity (needs splitting)
        if doc_pages > CAPACITY_16MM:
            logger.allocation(f"Document exceeds roll capacity, will be split across rolls", 
                           doc_name=doc_name, 
                           pages=doc_pages,
                           capacity=CAPACITY_16MM)
            
            # Document requires splitting regardless of new policy
            pages_left_to_allocate = doc_pages
            start_page = 1
            doc_roll_count = 0
            
            # Continue allocating pages until the entire document is allocated
            while pages_left_to_allocate > 0:
                current_roll = film_rolls["rolls"][str(current_roll_id)]
                
                # Calculate how many pages can fit in the current roll
                pages_to_allocate = min(pages_left_to_allocate, current_roll["pagesRemaining"])
                
                if pages_to_allocate > 0:
                    end_page = start_page + pages_to_allocate - 1
                    
                    # Get the current document index for this roll and increment
                    document_index = current_roll.get("next_document_index", 1)
                    current_roll["next_document_index"] = document_index + 1
                    
                    # Calculate frame numbers for this document segment
                    start_frame = current_roll["pagesUsed"] + 1
                    end_frame = start_frame + pages_to_allocate - 1
                    
                    # Generate blip string
                    film_number = current_roll["film_number"] if "film_number" in current_roll else "00000000"
                    blip = generate_blip(film_number, document_index, start_frame)
                    
                    # Add document to the roll
                    current_roll["documents"][doc_name] = {
                        "pages": pages_to_allocate,
                        "pagerange": [start_page, end_page],
                        "frameRange": [start_frame, end_frame],
                        "hasOversized": False,
                        "document_index": document_index,
                        "path": document_pages[doc_name].get("path", ""),
                        "blip": blip  # Add blip to document data
                    }
                    
                    # Update roll statistics
                    current_roll["pagesUsed"] += pages_to_allocate
                    current_roll["pagesRemaining"] -= pages_to_allocate
                    
                    #logger.debug(f"Updated roll statistics", 
                    #          roll_id=current_roll_id,
                    #          pages_used=current_roll["pagesUsed"],
                    #          pages_remaining=current_roll["pagesRemaining"])
                    
                    # Update tracking variables
                    pages_left_to_allocate -= pages_to_allocate
                    start_page = end_page + 1
                    doc_roll_count += 1
                
                # If we need more space and there are still pages to allocate, create a new roll
                if pages_left_to_allocate > 0:
                    # Mark the document as split
                    split_documents.add(doc_name)
                    current_roll["hasSplitDocuments"] = True
                    
                    logger.allocation(f"Document still needs more rolls for allocation", 
                                   doc_name=doc_name, 
                                   pages_remaining=pages_left_to_allocate)
                    
                    # Create a new roll
                    current_roll_id += 1
                    film_rolls["rolls"][str(current_roll_id)] = {
                        "pages": CAPACITY_16MM,
                        "pagesUsed": 0,
                        "pagesRemaining": CAPACITY_16MM,
                        "documents": {},
                        "hasSplitDocuments": False,
                        "isPartial": False,
                        "partialRollInfo": None,
                        "film_number": None,
                        "temp_roll_id": None,
                        "status": "active",
                        "creation_date": datetime.now().isoformat(),
                        "next_document_index": 1  # Reset document index for new roll
                    }
                    
                    logger.film(f"Created new roll {current_roll_id} with capacity {CAPACITY_16MM}")
        else:
            # Normal sized document - don't split unless necessary
            current_roll = film_rolls["rolls"][str(current_roll_id)]
            
            # Check if this document fits completely in the current roll
            if doc_pages <= current_roll["pagesRemaining"]:
                # It fits completely - allocate it
                # Get the current document index for this roll and increment
                document_index = current_roll.get("next_document_index", 1)
                current_roll["next_document_index"] = document_index + 1
                
                # Calculate frame numbers for this document
                start_frame = current_roll["pagesUsed"] + 1
                end_frame = start_frame + doc_pages - 1
                
                # Generate blip string
                film_number = current_roll["film_number"] if "film_number" in current_roll else "00000000"
                blip = generate_blip(film_number, document_index, start_frame)
                
                # Add document to the roll
                current_roll["documents"][doc_name] = {
                    "pages": doc_pages,
                    "pagerange": [1, doc_pages],
                    "frameRange": [start_frame, end_frame],
                    "hasOversized": False,
                    "document_index": document_index,
                    "path": document_pages[doc_name].get("path", ""),
                    "blip": blip  # Add blip to document data
                }
                
                # Update roll statistics
                current_roll["pagesUsed"] += doc_pages
                current_roll["pagesRemaining"] -= doc_pages
                
                #logger.debug(f"Updated roll statistics", 
                #          roll_id=current_roll_id,
                #          pages_used=current_roll["pagesUsed"],
                #          pages_remaining=current_roll["pagesRemaining"])
                
                # Document fits on a single roll
                document_pages[doc_name]["isSplit"] = False
                document_pages[doc_name]["rollCount"] = 1
            else:
                # Document doesn't fit in current roll - need to create a new roll
                logger.warning(f"Document doesn't fit in current roll, creating new roll", 
                               doc_name=doc_name, 
                               pages=doc_pages,
                               current_roll_remaining=current_roll["pagesRemaining"])
                
                # Mark current roll as partial
                current_roll["isPartial"] = True
                current_roll["partialRollInfo"] = {
                    "remainingCapacity": current_roll["pagesRemaining"],
                    "usableCapacity": current_roll["pagesRemaining"] - TEMP_ROLL_PADDING_16MM,
                    "isAvailable": True,
                    "createdFrom": None,
                    "usedBy": None,
                    "creation_date": datetime.now().isoformat()
                }
                
                logger.film(f"Created partial roll", 
                          roll_id=current_roll_id,
                          remaining_capacity=current_roll["pagesRemaining"],
                          usable_capacity=current_roll["pagesRemaining"] - TEMP_ROLL_PADDING_16MM)
                
                # Create a new roll
                current_roll_id += 1
                film_rolls["rolls"][str(current_roll_id)] = {
                    "pages": CAPACITY_16MM,
                    "pagesUsed": 0,
                    "pagesRemaining": CAPACITY_16MM,
                    "documents": {},
                    "hasSplitDocuments": False,
                    "isPartial": False,
                    "partialRollInfo": None,
                    "film_number": None,
                    "temp_roll_id": None,
                    "status": "active",
                    "creation_date": datetime.now().isoformat(),
                    "next_document_index": 1  # Reset document index for new roll
                }
                
                logger.film(f"Created new roll {current_roll_id} with capacity {CAPACITY_16MM}")
                
                # Now add the document to the new roll
                current_roll = film_rolls["rolls"][str(current_roll_id)]
                
                # Get the current document index for this roll and increment
                document_index = current_roll.get("next_document_index", 1)
                current_roll["next_document_index"] = document_index + 1
                
                # Calculate frame numbers for this document
                start_frame = 1  # Start from beginning of new roll
                end_frame = doc_pages
                
                # Generate blip string
                film_number = current_roll["film_number"] if "film_number" in current_roll else "00000000"
                blip = generate_blip(film_number, document_index, start_frame)
                
                # Add document to the roll
                current_roll["documents"][doc_name] = {
                    "pages": doc_pages,
                    "pagerange": [1, doc_pages],
                    "frameRange": [start_frame, end_frame],
                    "hasOversized": False,
                    "document_index": document_index,
                    "path": document_pages[doc_name].get("path", ""),
                    "blip": blip  # Add blip to document data
                }
                
                # Update roll statistics
                current_roll["pagesUsed"] += doc_pages
                current_roll["pagesRemaining"] -= doc_pages
                
                #logger.debug(f"Updated roll statistics", 
                #          roll_id=current_roll_id,
                #          pages_used=current_roll["pagesUsed"],
                #          pages_remaining=current_roll["pagesRemaining"])
                
                # Document fits on a single roll (the new one)
                document_pages[doc_name]["isSplit"] = False
                document_pages[doc_name]["rollCount"] = 1
        
        # After allocating all pages, mark if this document is split across rolls (only for documents > CAPACITY_16MM)
        if doc_pages > CAPACITY_16MM:
            doc_roll_count = len([roll_id for roll_id, roll_data in film_rolls["rolls"].items() 
                             if doc_name in roll_data.get("documents", {})])
                             
            if doc_roll_count > 1:
                # Mark the document as split
                document_pages[doc_name]["isSplit"] = True
                document_pages[doc_name]["rollCount"] = doc_roll_count
                
                logger.document(f"Large document is split across rolls", 
                            doc_name=doc_name, 
                            roll_count=doc_roll_count)
            else:
                document_pages[doc_name]["isSplit"] = False
                document_pages[doc_name]["rollCount"] = 1

    # Check if the last roll is a partial roll
    if film_rolls["rolls"][str(current_roll_id)]["pagesRemaining"] > 0:
        film_rolls["rolls"][str(current_roll_id)]["isPartial"] = True
        film_rolls["rolls"][str(current_roll_id)]["partialRollInfo"] = {
            "remainingCapacity": film_rolls["rolls"][str(current_roll_id)]["pagesRemaining"],
            "usableCapacity": film_rolls["rolls"][str(current_roll_id)]["pagesRemaining"] - TEMP_ROLL_PADDING_16MM,
            "isAvailable": True,
            "createdFrom": None,
            "usedBy": None,
            "creation_date": datetime.now().isoformat()
        }
        
        logger.film(f"Last roll is partial", 
                  roll_id=current_roll_id,
                  remaining_capacity=film_rolls["rolls"][str(current_roll_id)]["pagesRemaining"],
                  usable_capacity=film_rolls["rolls"][str(current_roll_id)]["pagesRemaining"] - TEMP_ROLL_PADDING_16MM)

    # Add detailed information about split documents
    logger.debug(f"Creating detailed information for {len(split_documents)} split documents")
    
    film_rolls["splitDocumentsDetails"] = {}
    for doc_name in split_documents:
        film_rolls["splitDocumentsDetails"][doc_name] = []
        # Find all rolls containing this document
        for roll_id, roll_data in film_rolls["rolls"].items():
            if roll_id.isdigit() and doc_name in roll_data.get("documents", {}):
                film_rolls["splitDocumentsDetails"][doc_name].append({
                    "roll": roll_id,
                    "pageRange": roll_data["documents"][doc_name]["pagerange"],
                    "frameRange": roll_data["documents"][doc_name]["frameRange"],
                })
                
                logger.debug(f"Split document segment", 
                           doc_name=doc_name,
                           roll_id=roll_id,
                           page_range=roll_data["documents"][doc_name]["pagerange"],
                           frame_range=roll_data["documents"][doc_name]["frameRange"])
    
    # Add information about partial rolls
    logger.debug("Creating information about partial rolls")
    
    film_rolls["partialRolls"] = []
    for roll_id, roll_data in film_rolls["rolls"].items():
        if roll_id.isdigit() and roll_data.get("isPartial", False):
            film_rolls["partialRolls"].append({
                "roll_id": roll_id,
                "remainingCapacity": roll_data["partialRollInfo"]["remainingCapacity"],
                "usableCapacity": roll_data["partialRollInfo"]["usableCapacity"],
                "isAvailable": roll_data["partialRollInfo"]["isAvailable"],
                "creation_date": roll_data["partialRollInfo"]["creation_date"]
            })
            
            #logger.film(f"Added partial roll to tracking list", 
            #          roll_id=roll_id,
            #          remaining_capacity=roll_data["partialRollInfo"]["remainingCapacity"],
            #          usable_capacity=roll_data["partialRollInfo"]["usableCapacity"])
    
    logger.film(f"Added {len(film_rolls['partialRolls'])} partial rolls to tracking list")

    # Update statistics
    film_rolls["statistics"]["total_rolls"] = current_roll_id
    film_rolls["statistics"]["total_pages"] = sum(roll["pagesUsed"] for roll in film_rolls["rolls"].values() if isinstance(roll, dict))
    film_rolls["statistics"]["total_partial_rolls"] = len(film_rolls["partialRolls"])
    film_rolls["statistics"]["total_split_documents"] = len(split_documents)
    
    logger.success(f"16mm allocation complete", 
                 total_rolls=current_roll_id,
                 total_pages=film_rolls["statistics"]["total_pages"],
                 total_partial_rolls=film_rolls["statistics"]["total_partial_rolls"],
                 total_split_documents=film_rolls["statistics"]["total_split_documents"])
    
    return film_rolls

def has_oversizes(document_pages, parent_folder_name, folder_name, project_info=None) -> Dict[str, Any]:
    """
    Allocate documents to film rolls when there are oversized pages.
    Uses 16mm for all pages and 35mm for oversized pages.
    
    Returns:
        dict: Film rolls allocation information
    """
    logger.section("FILM ALLOCATION - WITH OVERSIZED PAGES")
    logger.film("Starting allocation for documents with oversized pages")
    

    # Extract archive_id from project_info
    archive_id = "Unknown"
    if project_info and parent_folder_name in project_info:
        archive_id = project_info[parent_folder_name].get("archiveId", "Unknown")
    
    # Debug logging to check if document_pages is empty or missing oversized flags
    logger.debug(f"Debug document_pages: {len(document_pages)} documents found")
    oversized_count = sum(1 for doc in document_pages.values() if doc.get('oversized', False))
    logger.debug(f"Debug document_pages: {oversized_count} documents marked as oversized")
    if oversized_count == 0:
        logger.warning("No documents marked as oversized despite project having oversized flag")
    
    film_rolls: Dict[str, Any] = {
        "metadata": {
            "archive_id": archive_id,
            "project_name": folder_name,
            "creation_date": datetime.now().isoformat(),
            "version": "1.0"
        },
        "16mm": {
            "rolls": {},
            "splitDocumentsDetails": {},
            "partialRolls": [],
            "statistics": {
                "total_rolls": 0,
                "total_pages": 0,
                "total_partial_rolls": 0,
                "total_split_documents": 0
            }
        },
        "35mm": {
            "rolls": {},
            "splitDocumentsDetails": {},
            "partialRolls": [],
            "statistics": {
                "total_rolls": 0,
                "total_pages": 0,
                "total_partial_rolls": 0,
                "total_split_documents": 0
            }
        }
    }
    
    logger.film("Initializing 16mm film allocation")
    
    # Track which documents are split across rolls
    split_documents_16mm: Set[str] = set()
    
    # Sort documents alphabetically
    sorted_documents = sorted(document_pages.keys())
    logger.debug(f"Processing {len(sorted_documents)} documents in alphabetical order")
    
    # Start progress tracking
    logger.start_progress(len(sorted_documents), prefix="Allocating to 16mm:", suffix="Complete")
    
    # Initialize structure for 16mm
    current_roll_id_16mm = 1
    
    # Initialize the first 16mm roll
    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)] = {
        "pages": CAPACITY_16MM,
        "pagesUsed": 0,
        "pagesRemaining": CAPACITY_16MM,
        "documents": {},
        "hasSplitDocuments": False,
        "isPartial": False,
        "partialRollInfo": None,
        "film_number": None,
        "temp_roll_id": None,
        "status": "active",
        "creation_date": datetime.now().isoformat(),
        "next_document_index": 1  # Track the next document index for this roll
    }
    
    logger.film(f"Created 16mm roll {current_roll_id_16mm} with capacity {CAPACITY_16MM}")
    
    # Process each document in alphabetical order for 16mm allocation
    for doc_idx, doc_name in enumerate(sorted_documents):
        # Update the progress for each document
        logger.update_progress(doc_idx + 1)
        
        doc_data = document_pages[doc_name]
        doc_pages = doc_data["pages"]
        
        # Get ranges and reference pages for this document
        ranges = doc_data.get("ranges", [])
        reference_pages = doc_data.get("references", {}).get("pages", [])
        reference_count = doc_data.get("references", {}).get("totalReferences", 0)

        total_pages_with_refs = doc_pages + reference_count
        
        logger.document(f"Processing document for 16mm allocation", 
                      doc_name=doc_name, 
                      pages=total_pages_with_refs,
                      has_oversized=bool(ranges),
                      ref_count=reference_count)
        
        # Mark if the document has oversized pages
        is_oversized = bool(ranges)
        
        # If there are no oversized pages or ranges in this document,
        # handle it exactly like in no_oversizes()
        if not ranges:
            # Check if document exceeds roll capacity (needs splitting)
            if total_pages_with_refs > CAPACITY_16MM:
                logger.allocation(f"Document exceeds roll capacity, will be split across rolls", 
                           doc_name=doc_name, 
                           pages=total_pages_with_refs,
                           capacity=CAPACITY_16MM)
                
                # Document requires splitting regardless of new policy
                pages_left_to_allocate = total_pages_with_refs
                start_page = 1
                doc_roll_count = 0
                
                # Continue allocating pages until the entire document is allocated
                while pages_left_to_allocate > 0:
                    current_roll = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]
                    
                    # Calculate how many pages can fit in the current roll
                    pages_to_allocate = min(pages_left_to_allocate, current_roll["pagesRemaining"])
                    
                    if pages_to_allocate > 0:
                        # Allocate pages to the current roll
                        end_page = start_page + pages_to_allocate - 1
                        
                        # Calculate frame numbers for this document segment
                        start_frame = current_roll["pagesUsed"] + 1
                        end_frame = start_frame + pages_to_allocate - 1
                        
                        # Generate blip string
                        film_number = current_roll["film_number"] if "film_number" in current_roll else "00000000"
                        blip = generate_blip(film_number, document_index, start_frame)
                        
                        # Add document to the roll
                        if doc_name not in current_roll["documents"]:
                            current_roll["documents"][doc_name] = {
                                "pages": pages_to_allocate,
                                "pagerange": [start_page, end_page],
                                "frameRange": [start_frame, end_frame],
                                "hasOversized": is_oversized,
                                "path": document_pages[doc_name].get("path", ""),
                                "blip": blip  # Add blip to document data
                            }
                        else:
                            # Update existing entry
                            current_roll["documents"][doc_name]["pages"] += pages_to_allocate
                            current_roll["documents"][doc_name]["pagerange"][1] = end_page
                            current_roll["documents"][doc_name]["frameRange"][1] = end_frame
                        
                        # Update roll statistics
                        current_roll["pagesUsed"] += pages_to_allocate
                        current_roll["pagesRemaining"] -= pages_to_allocate
                        
                        # Update tracking variables
                        pages_left_to_allocate -= pages_to_allocate
                        start_page = end_page + 1
                        doc_roll_count += 1
                    
                    # If we need more space and there are still pages to allocate, create a new roll
                    if pages_left_to_allocate > 0:
                        # Mark the document as split
                        split_documents_16mm.add(doc_name)
                        current_roll["hasSplitDocuments"] = True
                        
                        logger.allocation(f"Document still needs more rolls for allocation", 
                                      doc_name=doc_name, 
                                      pages_remaining=pages_left_to_allocate)
                        
                        # Create a new roll
                        current_roll_id_16mm += 1
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)] = {
                            "pages": CAPACITY_16MM,
                            "pagesUsed": 0,
                            "pagesRemaining": CAPACITY_16MM,
                            "documents": {},
                            "hasSplitDocuments": False,
                            "isPartial": False,
                            "partialRollInfo": None,
                            "film_number": None,
                            "temp_roll_id": None,
                            "status": "active",
                            "creation_date": datetime.now().isoformat(),
                            "next_document_index": 1  # Reset document index for new roll
                        }
                        
                        logger.film(f"Created new roll {current_roll_id_16mm} with capacity {CAPACITY_16MM}")
                
                # Mark document as split across rolls if it spans multiple rolls
                if doc_roll_count > 1:
                    document_pages[doc_name]["isSplit"] = True
                    document_pages[doc_name]["rollCount"] = doc_roll_count
                    
                    logger.document(f"Large document is split across rolls", 
                                 doc_name=doc_name, 
                                 roll_count=doc_roll_count)
                else:
                    document_pages[doc_name]["isSplit"] = False
                    document_pages[doc_name]["rollCount"] = 1
            else:
                # Normal sized document - don't split unless necessary
                current_roll = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]
                
                # Check if this document fits completely in the current roll
                if total_pages_with_refs <= current_roll["pagesRemaining"]:
                    # It fits completely - allocate it
                    # Get the current document index for this roll and increment
                    document_index = current_roll.get("next_document_index", 1)
                    current_roll["next_document_index"] = document_index + 1
                    
                    # Calculate frame numbers for this document
                    start_frame = current_roll["pagesUsed"] + 1
                    end_frame = start_frame + total_pages_with_refs - 1
                    
                    # Generate blip string
                    film_number = current_roll["film_number"] if "film_number" in current_roll else "00000000"
                    blip = generate_blip(film_number, document_index, start_frame)
                    
                    # Add document to the roll
                    current_roll["documents"][doc_name] = {
                        "pages": total_pages_with_refs,
                        "pagerange": [1, total_pages_with_refs],
                        "frameRange": [start_frame, end_frame],
                        "hasOversized": is_oversized,
                        "document_index": document_index,
                        "path": document_pages[doc_name].get("path", ""),
                        "blip": blip  # Add blip to document data
                    }
                    
                    # Update roll statistics
                    current_roll["pagesUsed"] += total_pages_with_refs
                    current_roll["pagesRemaining"] -= total_pages_with_refs
                    
                    #logger.debug(f"Updated roll statistics", 
                    #          roll_id=current_roll_id_16mm,
                    #          pages_used=current_roll["pagesUsed"],
                    #          pages_remaining=current_roll["pagesRemaining"])
                    
                    # Document fits on a single roll
                    document_pages[doc_name]["isSplit"] = False
                    document_pages[doc_name]["rollCount"] = 1
                else:
                    # Document doesn't fit in current roll - need to create a new roll
                    logger.allocation(f"Document doesn't fit in current roll, creating new roll", 
                                   doc_name=doc_name, 
                                   pages=total_pages_with_refs,
                                   current_roll_remaining=current_roll["pagesRemaining"])
                    
                    # Mark current roll as partial
                    current_roll["isPartial"] = True
                    current_roll["partialRollInfo"] = {
                        "remainingCapacity": current_roll["pagesRemaining"],
                        "usableCapacity": current_roll["pagesRemaining"] - TEMP_ROLL_PADDING_16MM,
                        "isAvailable": True,
                        "createdFrom": None,
                        "usedBy": None,
                        "creation_date": datetime.now().isoformat()
                    }
                    
                    logger.film(f"Created partial roll", 
                              roll_id=current_roll_id_16mm,
                              remaining_capacity=current_roll["pagesRemaining"],
                              usable_capacity=current_roll["pagesRemaining"] - TEMP_ROLL_PADDING_16MM)
                    
                    # Create a new roll
                    current_roll_id_16mm += 1
                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)] = {
                        "pages": CAPACITY_16MM,
                        "pagesUsed": 0,
                        "pagesRemaining": CAPACITY_16MM,
                        "documents": {},
                        "hasSplitDocuments": False,
                        "isPartial": False,
                        "partialRollInfo": None,
                        "film_number": None,
                        "temp_roll_id": None,
                        "status": "active",
                        "creation_date": datetime.now().isoformat(),
                        "next_document_index": 1  # Reset document index for new roll
                    }
                    
                    logger.film(f"Created new roll {current_roll_id_16mm} with capacity {CAPACITY_16MM}")
                    
                    # Now add the document to the new roll
                    current_roll = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]
                    
                    # Get the current document index for this roll and increment
                    document_index = current_roll.get("next_document_index", 1)
                    current_roll["next_document_index"] = document_index + 1
                    
                    # Calculate frame numbers for this document
                    start_frame = 1  # Start from beginning of new roll
                    end_frame = total_pages_with_refs
                    
                    # Generate blip string
                    film_number = current_roll["film_number"] if "film_number" in current_roll else "00000000"
                    blip = generate_blip(film_number, document_index, start_frame)
                    
                    # Add document to the roll
                    current_roll["documents"][doc_name] = {
                        "pages": total_pages_with_refs,
                        "pagerange": [1, total_pages_with_refs],
                        "frameRange": [start_frame, end_frame],
                        "hasOversized": is_oversized,
                        "document_index": document_index,
                        "path": document_pages[doc_name].get("path", ""),
                        "blip": blip  # Add blip to document data
                    }
                    
                    # Update roll statistics
                    current_roll["pagesUsed"] += total_pages_with_refs
                    current_roll["pagesRemaining"] -= total_pages_with_refs
                    
                    #logger.debug(f"Updated roll statistics", 
                    #          roll_id=current_roll_id_16mm,
                    #          pages_used=current_roll["pagesUsed"],
                    #          pages_remaining=current_roll["pagesRemaining"])
                    
                    # Document fits on a single roll (the new one)
                    document_pages[doc_name]["isSplit"] = False
                    document_pages[doc_name]["rollCount"] = 1
        else:
            # Document has oversized pages that need special handling
            
            # Create a list of segments to allocate
            segments = []
            
            # Start with page 1
            current_page = 1
            total_pages_with_refs = doc_pages + reference_count
            
            # For each range and reference page, create segments
            for i, (range_start, range_end) in enumerate(ranges):
                # First, add regular pages before the range (if any)
                if current_page < range_start:
                    segment_pages = range_start - current_page
                    segments.append({
                        "type": "regular",
                        "start": current_page,
                        "end": range_start - 1,
                        "pages": segment_pages
                    })
                
                # Then add the atomic unit (reference page + range)
                range_pages = range_end - range_start + 1
                segments.append({
                    "type": "atomic",
                    "ref_position": reference_pages[i] if i < len(reference_pages) else None,
                    "range_start": range_start,
                    "range_end": range_end,
                    "start": range_start,
                    "end": range_end + 1,
                    "pages": range_pages + 1
                })
                
                # Update current page position
                current_page = range_end + 1
            
            # Add any remaining regular pages after the last range
            if current_page <= doc_pages:
                remaining_pages = doc_pages - current_page + 1
                segments.append({
                    "type": "regular",
                    "start": current_page,
                    "end": doc_pages,
                    "pages": remaining_pages
                })
            
            # Now allocate segments to rolls
            adjusted_start = 1
            
            for segment in segments:
                # Adjust segment start/end to account for previously added reference pages
                segment_size = segment["pages"]
                segment["adjusted_start"] = adjusted_start
                segment["adjusted_end"] = adjusted_start + segment_size - 1
                
                # Check if this segment fits in the current roll
                if film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] >= segment_size:
                    # It fits in the current roll
                    
                    # Calculate frame numbers for this segment
                    start_frame = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesUsed"] + 1
                    end_frame = start_frame + segment_size - 1
                    
                    if doc_name not in film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"]:
                        # First segment of this document in this roll
                        # Get the current document index for this roll and increment
                        document_index = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)].get("next_document_index", 1)
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["next_document_index"] = document_index + 1
                        
                        film_number = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["film_number"] if "film_number" in film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)] else "00000000"
                        blip = generate_blip(film_number, document_index, start_frame)
                        
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name] = {
                            "pages": segment_size,
                            "pagerange": [segment["adjusted_start"], segment["adjusted_end"]],
                            "frameRange": [start_frame, end_frame],
                            "hasOversized": is_oversized,
                            "document_index": document_index,  # Add document index
                            "path": document_pages[doc_name].get("path", ""),  # Add path from document_pages
                            "blip": blip  # Add blip to document data
                        }
                        
                        # Add oversized metadata if this document has oversized pages
                        if is_oversized:
                            film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["readable_pages"] = document_pages[doc_name]["readable_pages"]
                            film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["oversized_ranges"] = document_pages[doc_name]["ranges"]
                            film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["reference_positions"] = document_pages[doc_name]["references"]["pages"]
                            film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["adjusted_ranges"] = document_pages[doc_name]["adjusted_ranges"]
                    
                            logger.allocation(f"Allocating document with oversized pages to roll", 
                                doc_name=doc_name, 
                                roll_id=current_roll_id_16mm,
                                pages=segment_size, 
                                segment_type=segment["type"],
                                frame_range=[start_frame, end_frame])
                    else:
                        # Extend existing segment in this roll
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["pages"] += segment_size
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["pagerange"][1] = segment["adjusted_end"]
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["frameRange"][1] = end_frame
                        
                        # Ensure document_index exists for existing segments
                        if "document_index" not in film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]:
                            document_index = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)].get("next_document_index", 1)
                            film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["next_document_index"] = document_index + 1
                            film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["document_index"] = document_index
                    
                    # Update roll statistics
                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesUsed"] += segment_size
                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] -= segment_size
                else:
                    # Segment doesn't fit in current roll - need a new roll
                    
                    # If this isn't the first segment, mark as split
                    if segment != segments[0]:
                        split_documents_16mm.add(doc_name)
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["hasSplitDocuments"] = True
                    
                    # Check if the current roll is a partial roll
                    if film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] > 0:
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["isPartial"] = True
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["partialRollInfo"] = {
                            "remainingCapacity": film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"],
                            "usableCapacity": film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] - TEMP_ROLL_PADDING_16MM,
                            "isAvailable": True,
                            "createdFrom": None,
                            "usedBy": None,
                            "creation_date": datetime.now().isoformat()
                        }
                    
                    # Create a new roll
                    current_roll_id_16mm += 1
                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)] = {
                        "pages": CAPACITY_16MM,
                        "pagesUsed": 0,
                        "pagesRemaining": CAPACITY_16MM,
                        "documents": {},
                        "hasSplitDocuments": False,
                        "isPartial": False,
                        "partialRollInfo": None,
                        "film_number": None,
                        "temp_roll_id": None,
                        "status": "active",
                        "creation_date": datetime.now().isoformat(),
                        "next_document_index": 1  # Reset document index for new roll
                    }
                    
                    # Calculate frame numbers for this segment in the new roll
                    start_frame = 1
                    end_frame = segment_size
                    
                    # Add segment to the new roll
                    # Get the current document index for this roll and increment
                    document_index = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)].get("next_document_index", 1)
                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["next_document_index"] = document_index + 1
                    
                    film_number = film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["film_number"] if "film_number" in film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)] else "00000000"
                    blip = generate_blip(film_number, document_index, start_frame)

                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name] = {
                        "pages": segment_size,
                        "pagerange": [segment["adjusted_start"], segment["adjusted_end"]],
                        "frameRange": [start_frame, end_frame],
                        "hasOversized": is_oversized,
                        "document_index": document_index,  # Add document index
                        "path": document_pages[doc_name].get("path", ""),  # Add path from document_pages
                        "blip": blip  # Add blip to document data
                    }
                    
                    # Add oversized metadata if this document has oversized pages
                    if is_oversized:
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["readable_pages"] = document_pages[doc_name]["readable_pages"]
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["oversized_ranges"] = document_pages[doc_name]["ranges"]
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["reference_positions"] = document_pages[doc_name]["references"]["pages"]
                        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["documents"][doc_name]["adjusted_ranges"] = document_pages[doc_name]["adjusted_ranges"]
                    
                    # Update new roll statistics
                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesUsed"] += segment_size
                    film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] -= segment_size
                
                # Update adjusted page counter for next segment
                adjusted_start = segment["adjusted_end"] + 1
        
        # After allocating all segments, update last roll if document is split
        if doc_name in split_documents_16mm:
            # Update the last roll with split document flag too
            film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["hasSplitDocuments"] = True
    
    # Check if the last roll is a partial roll
    if film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] > 0:
        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["isPartial"] = True
        film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["partialRollInfo"] = {
            "remainingCapacity": film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"],
            "usableCapacity": film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] - TEMP_ROLL_PADDING_16MM,
            "isAvailable": True,
            "createdFrom": None,
            "usedBy": None,
            "creation_date": datetime.now().isoformat()
        }
        
        logger.film(f"Last 16mm roll is partial", 
                  roll_id=current_roll_id_16mm,
                  remaining_capacity=film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"],
                  usable_capacity=film_rolls["16mm"]["rolls"][str(current_roll_id_16mm)]["pagesRemaining"] - TEMP_ROLL_PADDING_16MM)

    # Add detailed information about split documents for 16mm
    logger.debug(f"Creating detailed information for {len(split_documents_16mm)} split documents")
    
    film_rolls["16mm"]["splitDocumentsDetails"] = {}
    for doc_name in split_documents_16mm:
        film_rolls["16mm"]["splitDocumentsDetails"][doc_name] = []
        # Find all rolls containing this document
        for roll_id, roll_data in film_rolls["16mm"]["rolls"].items():
            if roll_id.isdigit() and doc_name in roll_data["documents"]:
                film_rolls["16mm"]["splitDocumentsDetails"][doc_name].append({
                    "roll": roll_id,
                    "pageRange": roll_data["documents"][doc_name]["pagerange"],
                    "frameRange": roll_data["documents"][doc_name]["frameRange"],
                })
                
                logger.debug(f"Split document segment", 
                           doc_name=doc_name,
                           roll_id=roll_id,
                           page_range=roll_data["documents"][doc_name]["pagerange"],
                           frame_range=roll_data["documents"][doc_name]["frameRange"])
    
    # Add information about partial rolls for 16mm
    logger.debug("Creating information about partial rolls")
    
    film_rolls["16mm"]["partialRolls"] = []
    for roll_id, roll_data in film_rolls["16mm"]["rolls"].items():
        if roll_id.isdigit() and roll_data.get("isPartial", False):
            film_rolls["16mm"]["partialRolls"].append({
                "roll_id": roll_id,
                "remainingCapacity": roll_data["partialRollInfo"]["remainingCapacity"],
                "usableCapacity": roll_data["partialRollInfo"]["usableCapacity"],
                "isAvailable": roll_data["partialRollInfo"]["isAvailable"],
                "creation_date": roll_data["partialRollInfo"]["creation_date"]
            })
            
            logger.film(f"Added partial 16mm roll to tracking list", 
                      roll_id=roll_id,
                      remaining_capacity=roll_data["partialRollInfo"]["remainingCapacity"],
                      usable_capacity=roll_data["partialRollInfo"]["usableCapacity"])
    
    # Update 16mm statistics
    film_rolls["16mm"]["statistics"]["total_rolls"] = current_roll_id_16mm
    film_rolls["16mm"]["statistics"]["total_pages"] = sum(roll["pagesUsed"] for roll in film_rolls["16mm"]["rolls"].values() if isinstance(roll, dict))
    film_rolls["16mm"]["statistics"]["total_partial_rolls"] = len(film_rolls["16mm"]["partialRolls"])
    film_rolls["16mm"]["statistics"]["total_split_documents"] = len(split_documents_16mm)
    
    # Finish progress tracking
    logger.finish_progress()
    
    logger.success(f"16mm allocation complete", 
                 total_rolls=current_roll_id_16mm,
                 total_pages=film_rolls["16mm"]["statistics"]["total_pages"],
                 total_partial_rolls=film_rolls["16mm"]["statistics"]["total_partial_rolls"],
                 total_split_documents=film_rolls["16mm"]["statistics"]["total_split_documents"])
    
    # ===== 35mm Film Allocation =====
    logger.info("Starting 35mm film allocation using strict alphabetical approach")
    film_rolls["35mm"] = allocate_35mm_strict(document_pages, parent_folder_name, project_info)
    
    return film_rolls

def allocate_35mm_strict(document_pages, parent_folder_name, project_info=None) -> Dict[str, Any]:
    """
    Allocate 35mm film rolls in strict alphabetical order.
    
    Args:
        document_pages: Dictionary containing document information
        parent_folder_name: Name of the parent folder
        project_info: Optional dictionary containing project metadata
        
    Returns:
        dict: Film roll allocation information for 35mm
    """
    logger.section("35MM FILM ALLOCATION")
    logger.film("Starting 35mm film allocation using strict alphabetical approach")
    
    
    # Initialize 35mm allocation structure
    film_rolls_35mm = {
        "rolls": {},
        "splitDocumentsDetails": {},
        "partialRolls": [],
        "statistics": {
            "total_rolls": 0,
            "total_pages": 0,
            "total_oversized_pages": 0,
            "total_partial_rolls": 0,
            "total_split_documents": 0
        }
    }
    
    # Track which documents are split across rolls
    split_documents_35mm: Set[str] = set()
    
    # Count oversized pages
    oversized_count = sum(1 for doc in document_pages.values() if doc.get('oversized', False))
    oversized_docs = [doc_name for doc_name, doc in document_pages.items() if doc.get('oversized', False)]
    
    logger.info(f"Found {oversized_count} documents with oversized pages")
    
    if oversized_count == 0:
        logger.warning("No documents with oversized pages found, returning empty 35mm structure")
        return film_rolls_35mm
    
    # Sort oversized documents alphabetically
    sorted_oversized_docs = sorted(oversized_docs)
    logger.debug(f"Processing {len(sorted_oversized_docs)} oversized documents in alphabetical order")
    
    # Start progress tracking
    logger.start_progress(len(sorted_oversized_docs), prefix="Allocating to 35mm:", suffix="Complete")
    
    # Initialize structure for 35mm
    current_roll_id_35mm = 1
    
    # Initialize the first 35mm roll
    film_rolls_35mm["rolls"][str(current_roll_id_35mm)] = {
        "pages": CAPACITY_35MM,
        "pagesUsed": 0,
        "pagesRemaining": CAPACITY_35MM,
        "documents": {},
        "hasSplitDocuments": False,
        "isPartial": False,
        "partialRollInfo": None,
        "film_number": None,  # Will be assigned later
        "temp_roll_id": None,
        "status": "active",
        "creation_date": datetime.now().isoformat(),
        "next_document_index": 1  # Track the next document index for this roll
    }
    
    logger.film(f"Created 35mm roll {current_roll_id_35mm} with capacity {CAPACITY_35MM}")

    
    # Process each oversized document
    for doc_idx, doc_name in enumerate(sorted_oversized_docs):

        # Update progress
        logger.update_progress(doc_idx + 1)
        
        doc_data = document_pages[doc_name]
        
        # Get oversized ranges and total oversized pages
        ranges = doc_data.get("ranges", [])
        total_oversized_pages = sum(end - start + 1 for start, end in ranges)
        oversized_ranges = doc_data.get("ranges", [])
        total_pages_with_refs = total_oversized_pages + len(oversized_ranges)
        
        logger.document(f"Processing oversized document", 
                      doc_name=doc_name, 
                      ranges=ranges,
                      total_oversized_pages=total_pages_with_refs)
        
        if not ranges:
            logger.warning(f"Document marked as oversized but no ranges found")
            continue
        
        # Calculate if all oversized pages fit in current roll
        if film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"] >= total_pages_with_refs:
            # All pages fit in current roll
            
            # Calculate frame numbers
            # start_frame is the first frame number (1-based)
            # end_frame is the last frame number (start_frame + total pages - 1)
            # We subtract 1 because end_frame should be the last frame, not one past it
            start_frame = film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesUsed"] + 1
            end_frame = start_frame + total_pages_with_refs - 1
            
            # Get the document index for this roll
            document_index = film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["next_document_index"]
            film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["next_document_index"] = document_index + 1
            
            # Add to roll
            film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["documents"][doc_name] = {
                "pages": total_pages_with_refs,
                "pagerange": [1, total_pages_with_refs],  # Simplified page range for oversized
                "frameRange": [start_frame, end_frame],
                "hasOversized": True,
                "oversized_ranges": ranges,
                "document_index": document_index,  # Position on this roll
                "path": document_pages[doc_name].get("path", "")  # Add path from document_pages
            }
            
            # Update roll statistics
            film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesUsed"] += total_pages_with_refs
            film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"] -= total_pages_with_refs
            
            logger.debug(f"Added document {doc_name} to 35mm roll {current_roll_id_35mm}")
            
        else:
            # Document needs to be split across rolls
            split_documents_35mm.add(doc_name)
            film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["hasSplitDocuments"] = True
            
            logger.document(f"Document needs to be split across 35mm rolls", 
                          doc_name=doc_name, 
                          total_pages=total_pages_with_refs,
                          remaining_capacity=film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"])
            
            # First, use up what's left in the current roll
            remaining_capacity = film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"]
            
            if remaining_capacity > 0:
                # Calculate frame numbers for what fits in this roll
                start_frame = film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesUsed"] + 1
                end_frame = start_frame + remaining_capacity - 1
                
                # Get the document index for this roll
                document_index = film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["next_document_index"]
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["next_document_index"] = document_index + 1
                
                # Add to roll
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["documents"][doc_name] = {
                    "pages": remaining_capacity,
                    "pagerange": [1, remaining_capacity],  # Simplified for oversized
                    "frameRange": [start_frame, end_frame],
                    "hasOversized": True,
                    "is_segment": True,
                    "segment_info": {
                        "total_pages": total_pages_with_refs,
                        "segment_position": 1,
                        "total_segments": math.ceil(total_pages_with_refs / CAPACITY_35MM)
                    },
                    "document_index": document_index,  # Position on this roll
                    "path": document_pages[doc_name].get("path", "")  # Add path from document_pages
                }
                
                # Update roll statistics - roll is now full
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesUsed"] += remaining_capacity
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"] = 0
                
                logger.debug(f"Added first segment of document {doc_name} to 35mm roll {current_roll_id_35mm}")
            
            # Pages left to allocate
            pages_left = total_pages_with_refs - remaining_capacity
            start_page = remaining_capacity + 1
            segment_count = 1  # We've allocated one segment so far
            
            # Create new rolls as needed
            while pages_left > 0:
                # Mark the current roll as full (not partial)
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["isPartial"] = False
                
                # Create a new roll
                current_roll_id_35mm += 1
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)] = {
                    "pages": CAPACITY_35MM,
                    "pagesUsed": 0,
                    "pagesRemaining": CAPACITY_35MM,
                    "documents": {},
                    "hasSplitDocuments": False,
                    "isPartial": False,
                    "partialRollInfo": None,
                    "film_number": None,
                    "temp_roll_id": None,
                    "status": "active",
                    "creation_date": datetime.now().isoformat(),
                    "next_document_index": 1  # Reset document index for new roll
                }
                
                logger.film(f"Created new 35mm roll {current_roll_id_35mm} with capacity {CAPACITY_35MM}")
                
                # Calculate how many pages to put in this roll
                pages_to_allocate = min(pages_left, CAPACITY_35MM)
                end_page = start_page + pages_to_allocate - 1
                
                # Get the document index for this roll
                document_index = film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["next_document_index"]
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["next_document_index"] = document_index + 1
                
                # Add to roll
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["documents"][doc_name] = {
                    "pages": pages_to_allocate,
                    "pagerange": [start_page, end_page],
                    "frameRange": [1, pages_to_allocate],  # Starts from the beginning of the roll
                    "hasOversized": True,
                    "is_segment": True,
                    "segment_info": {
                        "total_pages": total_pages_with_refs,
                        "segment_position": segment_count + 1,
                        "total_segments": math.ceil(total_pages_with_refs / CAPACITY_35MM)
                    },
                    "document_index": document_index,  # Position on this roll
                    "path": document_pages[doc_name].get("path", "")  # Add path from document_pages
                }
                
                # Update roll statistics
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesUsed"] += pages_to_allocate
                film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"] -= pages_to_allocate
                
                # Update tracking variables
                pages_left -= pages_to_allocate
                start_page = end_page + 1
                segment_count += 1
                
                logger.debug(f"Added segment {segment_count} of document {doc_name} to 35mm roll {current_roll_id_35mm}")
    
    # Check if the last roll is a partial roll
    if film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"] > 0:
        film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["isPartial"] = True
        film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["partialRollInfo"] = {
            "remainingCapacity": film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"],
            "usableCapacity": film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"] - TEMP_ROLL_PADDING_35MM,
            "isAvailable": True,
            "createdFrom": None,
            "usedBy": None,
            "creation_date": datetime.now().isoformat()
        }
        
        logger.film(f"Last 35mm roll is partial", 
                  roll_id=current_roll_id_35mm,
                  remaining_capacity=film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"],
                  usable_capacity=film_rolls_35mm["rolls"][str(current_roll_id_35mm)]["pagesRemaining"] - TEMP_ROLL_PADDING_35MM)
    
    # Add detailed information about split documents for 35mm
    logger.debug(f"Creating detailed information for {len(split_documents_35mm)} split 35mm documents")
    
    film_rolls_35mm["splitDocumentsDetails"] = {}
    for doc_name in split_documents_35mm:
        film_rolls_35mm["splitDocumentsDetails"][doc_name] = []
        # Find all rolls containing this document
        for roll_id, roll_data in film_rolls_35mm["rolls"].items():
            if roll_id.isdigit() and doc_name in roll_data["documents"]:
                film_rolls_35mm["splitDocumentsDetails"][doc_name].append({
                    "roll": roll_id,
                    "pageRange": roll_data["documents"][doc_name]["pagerange"],
                    "frameRange": roll_data["documents"][doc_name]["frameRange"],
                    "segment_info": roll_data["documents"][doc_name].get("segment_info", {})
                })
                
                logger.debug(f"Split 35mm document segment", 
                           doc_name=doc_name,
                           roll_id=roll_id,
                           page_range=roll_data["documents"][doc_name]["pagerange"],
                           frame_range=roll_data["documents"][doc_name]["frameRange"])
    
    # Add information about partial rolls for 35mm
    logger.debug("Creating information about partial 35mm rolls")
    
    film_rolls_35mm["partialRolls"] = []
    for roll_id, roll_data in film_rolls_35mm["rolls"].items():
        if roll_id.isdigit() and roll_data.get("isPartial", False):
            film_rolls_35mm["partialRolls"].append({
                "roll_id": roll_id,
                "remainingCapacity": roll_data["partialRollInfo"]["remainingCapacity"],
                "usableCapacity": roll_data["partialRollInfo"]["usableCapacity"],
                "isAvailable": roll_data["partialRollInfo"]["isAvailable"],
                "creation_date": roll_data["partialRollInfo"]["creation_date"]
            })
            
            logger.film(f"Added partial 35mm roll to tracking list", 
                      roll_id=roll_id,
                      remaining_capacity=roll_data["partialRollInfo"]["remainingCapacity"],
                      usable_capacity=roll_data["partialRollInfo"]["usableCapacity"])
    
    # Update 35mm statistics
    film_rolls_35mm["statistics"]["total_rolls"] = current_roll_id_35mm
    film_rolls_35mm["statistics"]["total_pages"] = sum(roll["pagesUsed"] for roll in film_rolls_35mm["rolls"].values() if isinstance(roll, dict))
    film_rolls_35mm["statistics"]["total_oversized_pages"] = film_rolls_35mm["statistics"]["total_pages"]
    film_rolls_35mm["statistics"]["total_partial_rolls"] = len(film_rolls_35mm["partialRolls"])
    film_rolls_35mm["statistics"]["total_split_documents"] = len(split_documents_35mm)
    
    # Finish progress tracking
    logger.finish_progress()
    
    logger.success(f"35mm allocation complete", 
                 total_rolls=current_roll_id_35mm,
                 total_pages=film_rolls_35mm["statistics"]["total_pages"],
                 total_partial_rolls=film_rolls_35mm["statistics"]["total_partial_rolls"],
                 total_split_documents=film_rolls_35mm["statistics"]["total_split_documents"])
    
    return film_rolls_35mm

def initialize_index(document_pages: Dict[str, Any], comlist_path: str, film_rolls: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Initialize index for tracking document locations on film rolls.
    Only processes 16mm rolls (35mm rolls are intentionally excluded).
    
    Args:
        document_pages: Dictionary containing document information
        film_rolls: Optional dictionary containing film rolls allocation
        
    Returns:
        dict: Index data
    """
    
    logger.section("INITIALIZING INDEX")
    
    
    logger.info(f"Starting index initialization")
    
    # Initialize index data
    index_data = {
        "metadata": {
            "creation_date": datetime.now().isoformat(),
            "version": "1.0"
        },
        "index": []
    }
    
    # Create a dictionary to store barcode to ComID mappings
    barcode_to_comid = {}
    
    try:
        
        # Read the Excel file
        logger.info(f"Reading Comlist from {comlist_path}")
        try:
            # Try to connect to Excel file using xlwings
            wb = None
            try:
                # Try to use already open workbook
                wb = xw.books.active
                if Path(wb.fullname).resolve() != Path(comlist_path).resolve():
                    wb = xw.Book(comlist_path)
            except Exception:
                # Open the workbook directly
                wb = xw.Book(comlist_path)
            
            # Get the first worksheet
            ws = wb.sheets[0]
            
            # Get data range with potential barcode and ComID values
            # Assuming barcode is in column A and ComID is in column B
            used_range = ws.used_range
            if used_range:
                data = used_range.value
                
                # Skip header row if exists
                start_row = 1 if isinstance(data[0][0], str) and not data[0][0].isdigit() else 0
                
                # Extract barcode and ComID pairs
                for i in range(start_row, len(data)):
                    if i < len(data) and len(data[i]) >= 2:
                        barcode = str(data[i][0]) if data[i][0] is not None else None
                        com_id = data[i][1]
                        
                        # Convert ComID to integer if possible
                        if com_id is not None:
                            try:
                                # Handle case where Excel returns a float
                                if isinstance(com_id, float) and com_id.is_integer():
                                    com_id = int(com_id)
                                else:
                                    com_id = int(com_id)
                                
                                if barcode and com_id:
                                    barcode_to_comid[barcode] = com_id
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid ComID value for barcode {barcode}: {com_id}")
            
            logger.info(f"Successfully loaded {len(barcode_to_comid)} barcode-ComID mappings")
            
            # Close Excel if we opened it
            if wb:
                wb.app.quit()
            
        except FileNotFoundError:
            logger.warning(f"Comlist Excel file not found at {comlist_path}. Creating empty index.")
            barcode_to_comid = {}
        except Exception as e:
            logger.error(f"Error reading Comlist Excel file: {str(e)}. Creating empty index.")
            barcode_to_comid = {}
            if wb:
                try:
                    wb.app.quit()
                except:
                    pass
        
        # Use the film_rolls dictionary passed as an argument instead of loading from JSON
        if film_rolls is None:
            logger.error("film_rolls dictionary not provided. Cannot create index.")
            return index_data
        
        # Determine which rolls to process based on project structure
        # Note: Intentionally only processing 16mm rolls, excluding 35mm rolls
        if "16mm" in film_rolls:
            # Project with oversized pages - use only 16mm rolls
            logger.info("Project has oversized pages. Only processing 16mm rolls for index.")
            rolls_data = film_rolls["16mm"]["rolls"]
        elif "rolls" in film_rolls:
            # Standard project structure - process all rolls
            logger.info("Processing standard project rolls for index.")
            rolls_data = film_rolls["rolls"]
        else:
            logger.warning("Unknown film rolls structure. Cannot create index.")
            return index_data
        # Iterate through each roll
        for roll_id, roll_data in rolls_data.items():
            roll_id_int = int(roll_id)
            
            # Iterate through each document in this roll
            for doc_name, doc_data in roll_data.get("documents", {}).items():
                # Get document index (position on this roll)
                doc_index = doc_data.get("document_index", 0)
                
                # Get frame range for this document
                frame_range = doc_data.get("frameRange", [0, 0])
                
                # Get ComID from barcode_to_comid dictionary
                com_id = barcode_to_comid.get(doc_name, None)
                
                # If ComID is not found, generate a placeholder
                if com_id is None:
                    # Log document not found in Comlist Excel file
                    logger.warning(f"Document {doc_name} not found in Comlist Excel file")
                    # Use a placeholder ComID (negative roll_id to avoid conflicts)
                    com_id = -roll_id_int

                
                # After getting com_id from barcode_to_comid, update document_pages
                if doc_name in document_pages and com_id is not None:
                    document_pages[doc_name]["com_id"] = com_id
                
                # Create initial index array with [roll_id, frameRange_start, frameRange_end]
                initial_index = [roll_id_int, frame_range[0], frame_range[1]]
                
                # Create index entry with document index
                index_entry = [
                    doc_name,                # Barcode
                    com_id,                  # ComID
                    initial_index,           # Initial index [roll_id, frameRange_start, frameRange_end]
                    None,                    # Final index (to be filled later)
                    doc_index                # Add document index as an additional field
                ]
                
                # Add to index
                index_data["index"].append(index_entry)

                
                #logger.debug(f"Added index entry for document {doc_name} with ComID {com_id} and initial index {initial_index}")
        
        logger.success(f"Index initialization completed with {len(index_data['index'])} entries")
        
    except Exception as e:
        logger.error(f"Error initializing index: {str(e)}")
        index_data = {
            "metadata": {
                "creation_date": datetime.now().isoformat(),
                "version": "1.0",
                "error": str(e)
            },
            "index": []
        }
    
    return index_data


# --------------------------------  FILM NUMBERS ALLOCATION -------------------------------
"""
This section describes the film number allocation process.

1. Film Number Allocation Overview
Film numbers are allocated based on the location of the project (OU, DW, etc.) and follow a sequential pattern:
- OU location: Film numbers start with '1' (e.g., 10000001, 10000002)
- DW location: Film numbers start with '2' (e.g., 20000001, 20000002)
- Other locations: Film numbers start with '3' (e.g., 30000001, 30000002)

2. Roll Management and Capacity
For each film type:
- 16mm rolls: Capacity of 2900 pages with padding of 100 pages
- 35mm rolls: Capacity of 690 pages with padding of 100 pages

3. Partial Roll Handling
When a roll has remaining capacity after allocation:
- The roll is marked with `isPartial: true` 
- Details are stored in `partialRollInfo` including:
  - `remainingCapacity`: Total pages remaining on the roll
  - `usableCapacity`: Remaining capacity minus padding (TEMP_ROLL_PADDING)
  - `isAvailable`: Whether the roll can be used for future allocations
  - `createdFrom` and `usedBy`: References to track roll relationships
  - `creation_date`: Timestamp of when the partial roll was created

4. Roll Reuse Strategy
- For 16mm film: Each roll gets a unique film number, with no sharing across projects
- For 35mm film: Rolls can be reused across projects if they have sufficient remaining capacity
  and belong to the same location

5. Database Schema
The database tracks all rolls, projects, and documents with the following tables:

CREATE TABLE IF NOT EXISTS Projects (
    project_id INTEGER PRIMARY KEY,
    archive_id TEXT NOT NULL, 
    location TEXT,
    doc_type TEXT,
    path TEXT,
    folderName TEXT,
    oversized BOOLEAN,
    total_pages INTEGER,
    total_pages_with_refs INTEGER,
    date_created TEXT,
    data_dir TEXT,
    index_path TEXT
)

CREATE TABLE IF NOT EXISTS Rolls (
    roll_id INTEGER PRIMARY KEY,
    film_number TEXT,
    film_type TEXT,
    capacity INTEGER,
    pages_used INTEGER,
    pages_remaining INTEGER,
    status TEXT,
    project_id INTEGER,
    creation_date TEXT,
    source_temp_roll_id INTEGER NULL,
    created_temp_roll_id INTEGER NULL,
    film_number_source TEXT NULL,
    FOREIGN KEY (project_id) REFERENCES Projects(project_id),
    FOREIGN KEY (source_temp_roll_id) REFERENCES TempRolls(temp_roll_id),
    FOREIGN KEY (created_temp_roll_id) REFERENCES TempRolls(temp_roll_id)
)

CREATE TABLE IF NOT EXISTS TempRolls (
    temp_roll_id INTEGER PRIMARY KEY,
    film_type TEXT,
    capacity INTEGER,
    usable_capacity INTEGER,
    status TEXT,
    creation_date TEXT,
    source_roll_id INTEGER,
    used_by_roll_id INTEGER NULL,
    FOREIGN KEY (source_roll_id) REFERENCES Rolls(roll_id),
    FOREIGN KEY (used_by_roll_id) REFERENCES Rolls(roll_id)
)

CREATE TABLE IF NOT EXISTS Documents (
    document_id INTEGER PRIMARY KEY,
    document_name TEXT,
    com_id TEXT,
    roll_id INTEGER,
    page_range_start INTEGER,
    page_range_end INTEGER,
    is_oversized BOOLEAN,
    filepath TEXT,
    FOREIGN KEY (roll_id) REFERENCES Rolls(roll_id)
)
"""

def propagate_com_ids_and_assign_film_numbers(document_pages: Dict[str, Any], 
                           film_rolls: Dict[str, Any], 
                           index_data: Optional[Dict[str, Any]], 
                           project_data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Propagate com_id values from document_pages to film_rolls and assign film numbers to rolls.
    
    This function performs two main tasks:
    1. Copies com_id values from document_pages to the corresponding documents in film_rolls
    2. Assigns film numbers to all rolls in the film_rolls structure
    
    Args:
        document_pages: Dictionary containing document information with com_id values
        film_rolls: Dictionary containing film roll allocation
        index_data: Optional dictionary containing index data
        project_data: Dictionary with complete project data for database
        
    Returns:
        tuple: Updated (film_rolls, index_data) with com_ids propagated and film numbers assigned
    """
    
    logger.section("PROPAGATING COM_IDS AND ASSIGNING FILM NUMBERS")
    
    logger.info(f"Starting com_id propagation and film number assignment")
    
    # Propagate com_id values from document_pages to film_rolls
    logger.info("Propagating com_id values from document_pages to film_rolls")
    for doc_name, doc_data in document_pages.items():
        if "com_id" in doc_data:
            # Find this document in film_rolls structure
            if "16mm" in film_rolls:
                for roll_id, roll_data in film_rolls["16mm"]["rolls"].items():
                    if "documents" in roll_data and doc_name in roll_data["documents"]:
                        roll_data["documents"][doc_name]["com_id"] = doc_data["com_id"]
            if "35mm" in film_rolls:
                for roll_id, roll_data in film_rolls["35mm"]["rolls"].items():
                    if "documents" in roll_data and doc_name in roll_data["documents"]:
                        roll_data["documents"][doc_name]["com_id"] = doc_data["com_id"]
            if "rolls" in film_rolls:
                for roll_id, roll_data in film_rolls["rolls"].items():
                    if "documents" in roll_data and doc_name in roll_data["documents"]:
                        roll_data["documents"][doc_name]["com_id"] = doc_data["com_id"]
    
    # Log project information for debugging
    if project_data:
        logger.debug(f"Project data provided with archive_id: {project_data.get('archive_id', 'Unknown')}")
        logger.debug(f"Project contains oversized pages: {project_data.get('oversized', False)}")
        logger.debug(f"Project total pages: {project_data.get('total_pages', 0)} (with refs: {project_data.get('total_pages_with_refs', 0)})")
    else:
        logger.debug(f"No project data provided, will use data from film_rolls")
    
    # Basic validation of input data
    if not film_rolls:
        logger.error(f"Error: No film rolls provided for film number allocation")
        return film_rolls, index_data
    
    # Check film rolls structure
    has_16mm = "16mm" in film_rolls
    has_35mm = "35mm" in film_rolls
    has_standard = "rolls" in film_rolls
    
    logger.debug(f"Film rolls structure: 16mm={has_16mm}, 35mm={has_35mm}, standard={has_standard}")
    
    if has_16mm and has_35mm:
        # Project with oversized pages
        logger.debug(f"Processing project with oversized pages: {len(film_rolls['16mm']['rolls'])} 16mm rolls, {len(film_rolls['35mm']['rolls'])} 35mm rolls")
    elif has_standard:
        # Standard project without oversized pages
        logger.debug(f"Processing standard project: {len(film_rolls['rolls'])} rolls")
    
    # Call the core film number allocation function directly
    logger.debug(f"Calling allocate_film_numbers with project data")
    updated_film_rolls = allocate_film_numbers(film_rolls, project_data)
    
    # Update index_data with film numbers if provided
    updated_index_data = None
    if index_data:
        logger.debug(f"Updating index data with assigned film numbers")
        updated_index_data = update_index_data(index_data, updated_film_rolls)
    else:
        logger.debug(f"No index data provided, skipping index update")
    
    # Check if film_rolls content changed by looking for film numbers
    film_rolls_changed = False
    
    # Helper function to check if a roll has a film number
    def has_film_number(roll_data):
        return "film_number" in roll_data and roll_data["film_number"] is not None
    
    # Check if any rolls have film numbers
    if has_standard:
        for roll_id, roll_data in updated_film_rolls["rolls"].items():
            if has_film_number(roll_data):
                film_rolls_changed = True
                break
    elif has_16mm:
        for roll_id, roll_data in updated_film_rolls["16mm"]["rolls"].items():
            if has_film_number(roll_data):
                film_rolls_changed = True
                break
    elif has_35mm:
        for roll_id, roll_data in updated_film_rolls["35mm"]["rolls"].items():
            if has_film_number(roll_data):
                film_rolls_changed = True
                break
    
    # Log results for debugging
    if film_rolls_changed:
        logger.success(f"Film rolls updated with film numbers")
    else:
        logger.warning(f"Film rolls were not updated with film numbers, possible error in allocation")
        
    # Check if index_data content changed
    index_data_changed = False
    if updated_index_data and index_data:
        # Check if any entries have film numbers
        if "index" in updated_index_data and "index" in index_data:
            for entry in updated_index_data["index"]:
                if len(entry) > 1 and entry[1] is not None:
                    index_data_changed = True
                    break
    
    if index_data_changed:
        logger.success(f"Index data updated with film numbers")
    else:
        logger.warning(f"Index data was not updated or no index data provided")
    
    logger.success(f"Com_id propagation and film number assignment completed successfully")
    
    return updated_film_rolls, updated_index_data

def allocate_film_numbers(film_rolls, project_data=None) -> Dict[str, Any]:
    """
    Assign film numbers to rolls.
    
    Args:
        film_rolls: Dictionary containing film rolls allocation
        project_data: Optional dictionary containing project data
        
    Returns:
        dict: Updated film_rolls
    """
    logger.info(f"Starting film number allocation with DB persistence")
    
    # Create database connection
    conn = get_connection()
    
    try:
        # Begin transaction
        begin_transaction(conn)
        cursor = conn.cursor()
        
        # Insert project info into the Projects table
        project_id = None
        
        if project_data:
            # Check if project already exists
            cursor.execute(
                "SELECT project_id FROM Projects WHERE archive_id = ? AND path = ?",
                (project_data.get("archive_id", "Unknown"), project_data.get("path", ""))
            )
            result = cursor.fetchone()
            
            if result:
                project_id = result[0]
                logger.info(f"Found existing project with ID {project_id}")
                
            else:
                # Insert new project
                cursor.execute(
                    """INSERT INTO Projects 
                       (archive_id, location, doc_type, path, folderName, oversized, 
                       total_pages, total_pages_with_refs, date_created, data_dir, index_path) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        project_data.get("archive_id", "Unknown"),
                        project_data.get("location", "Unknown"),
                        project_data.get("doc_type", "Unknown"),
                        project_data.get("path", ""),
                        project_data.get("folderName", ""),
                        project_data.get("oversized", False),
                        project_data.get("total_pages", 0),
                        project_data.get("total_pages_with_refs", 0),
                        datetime.now().isoformat(),
                        project_data.get("data_dir", ""),
                        project_data.get("index_path", "")
                    )
                )
                project_id = cursor.lastrowid
                logger.info(f"Created new project with ID {project_id}")
        else:
            # No project data provided, create a minimal project entry
            cursor.execute(
                "INSERT INTO Projects (archive_id, date_created) VALUES (?, ?)",
                ("Unknown", datetime.now().isoformat())
            )
            project_id = cursor.lastrowid
            logger.info(f"Created minimal project with ID {project_id}")
        
        # Get count of existing temp rolls in database
        cursor.execute("SELECT COUNT(*) FROM TempRolls WHERE status = 'available'")
        temp_roll_count = cursor.fetchone()[0]
        logger.debug(f"Current database has {temp_roll_count} temp rolls")
        
        # Process 16mm rolls if they exist
        if "16mm" in film_rolls:
            logger.info(f"Processing 16mm rolls")
            process_16mm_rolls(cursor, film_rolls, project_id)
        
        # Process 35mm rolls if they exist
        if "35mm" in film_rolls:
            logger.info(f"Processing 35mm rolls")
            process_35mm_rolls(cursor, film_rolls, project_id)
            
        # Handle standard rolls structure (no 16mm/35mm separation)
        elif "rolls" in film_rolls:
            logger.info(f"Processing standard rolls (no 16mm/35mm separation)")
            # Get statistics
            total_rolls = len(film_rolls["rolls"])
            partial_rolls = sum(1 for roll_data in film_rolls["rolls"].values() if roll_data.get("isPartial", False))
            full_rolls = total_rolls - partial_rolls
            
            logger.info(f"Processing {total_rolls} standard rolls ({full_rolls} full, {partial_rolls} partial)")
            
            processed_count = 0
            assigned_new_number_count = 0
            used_temp_roll_count = 0
            created_temp_roll_count = 0
            
            # Process each standard roll (similar to process_16mm_rolls)
            for roll_id, roll_data in film_rolls["rolls"].items():
                if not roll_id.isdigit():
                    logger.debug(f"Skipping non-numeric roll ID: {roll_id}")
                    continue
                    
                # Check if film number already assigned
                if roll_data.get("film_number") is not None:
                    logger.debug(f"Roll {roll_id} already has film number {roll_data['film_number']}, skipping")
                    continue
                
                logger.info(f"Processing standard roll {roll_id}")
                if roll_data.get("isPartial", False):
                    logger.debug(f"Roll {roll_id} is a partial roll with {roll_data.get('pagesUsed', 0)} pages used")
                else:
                    logger.debug(f"Roll {roll_id} is a full roll with {roll_data.get('pagesUsed', 0)} pages used")
                
                # Calculate pages needed
                pages_needed = roll_data.get("pagesUsed", 0)
                logger.debug(f"Roll {roll_id} requires {pages_needed} pages")
                
                # Check if this is a partial roll that could use a temp roll
                is_partial = roll_data.get("isPartial", False)
                film_number = None
                temp_roll_id = None
                source_temp_roll = None
                
                if is_partial:
                    logger.info(f"Checking for temp rolls for partial roll {roll_id}")
                    # Try to find a suitable temp roll
                    temp_roll_result = find_suitable_temp_roll(cursor, pages_needed, "16mm")
                    
                    if temp_roll_result:
                        temp_roll_id, source_roll_id, usable_capacity = temp_roll_result
                        
                        logger.success(f"Found suitable temp roll {temp_roll_id} with {usable_capacity} capacity")
                        
                        # Always generate a new film number based on the current project location
                        location = get_project_location(cursor, project_id)
                        film_number = get_next_film_number(cursor, location)
                        
                        logger.info(f"Using temp roll {temp_roll_id} with {usable_capacity} capacity for partial standard roll {roll_id}")
                        
                        # Calculate remaining capacity after use
                        remaining_capacity = usable_capacity - pages_needed
                        logger.debug(f"After use: remaining capacity = {remaining_capacity}")
                        
                        # Format for logging
                        source_temp_roll = f"temp_roll_{temp_roll_id}"
                        used_temp_roll_count += 1
                        
                        # If there's enough remaining capacity, create a new temp roll from the remainder
                        if remaining_capacity >= TEMP_ROLL_MIN_USABLE_PAGES:
                            logger.info(f"Enough remaining capacity to create new temp roll: {remaining_capacity} >= {TEMP_ROLL_MIN_USABLE_PAGES}")
                            # Calculate usable capacity (apply any required padding)
                            usable_remainder = remaining_capacity
                            
                            # Insert roll first to get its ID
                            cursor.execute(
                                "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date, source_temp_roll_id, film_number_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (
                                    film_number,
                                    "16mm",
                                    usable_capacity,
                                    pages_needed,
                                    0,
                                    "active",
                                    project_id,
                                    roll_data.get("creation_date", datetime.now().isoformat()),
                                    temp_roll_id,
                                    "temp_roll"
                                )
                            )
                            roll_db_id = cursor.lastrowid
                            logger.debug(f"Created roll record in database with ID {roll_db_id}")
                            
                            # Mark the temp roll as used
                            mark_temp_roll_used(cursor, temp_roll_id, roll_db_id)
                            logger.debug(f"Marked temp roll {temp_roll_id} as used by roll {roll_db_id}")
                            
                            # Create a new temp roll from the remainder
                            new_temp_roll_id = create_temp_roll_from_remainder(
                                cursor, 
                                temp_roll_id, 
                                remaining_capacity, 
                                usable_remainder,
                                roll_db_id
                            )
                            
                            if new_temp_roll_id:
                                logger.success(f"Created new temp roll {new_temp_roll_id} from remainder with {usable_remainder} usable capacity")
                                created_temp_roll_count += 1
                                
                                # Update roll with created temp roll ID
                                cursor.execute(
                                    "UPDATE Rolls SET created_temp_roll_id = ? WHERE roll_id = ?",
                                    (new_temp_roll_id, roll_db_id)
                                )
                                logger.debug(f"Updated roll {roll_db_id} with created temp roll ID {new_temp_roll_id}")
                        else:
                            # Not enough remaining capacity to create a temp roll
                            # Just use the entire temp roll
                            cursor.execute(
                                "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date, source_temp_roll_id, film_number_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (
                                    film_number,
                                    "16mm",
                                    usable_capacity,
                                    pages_needed,
                                    usable_capacity - pages_needed,
                                    "active",
                                    project_id,
                                    roll_data.get("creation_date", datetime.now().isoformat()),
                                    temp_roll_id,
                                    "temp_roll"
                                )
                            )
                            roll_db_id = cursor.lastrowid
                            logger.debug(f"Created roll record in database with ID {roll_db_id}")
                            
                            # Mark the temp roll as used
                            mark_temp_roll_used(cursor, temp_roll_id, roll_db_id)
                            logger.debug(f"Marked temp roll {temp_roll_id} as used by roll {roll_db_id}")
                
                # If no temp roll was found or if this is a full roll, use a new film number
                if film_number is None:
                    # Get project location
                    location = get_project_location(cursor, project_id)
                    film_number = get_next_film_number(cursor, location)
                    assigned_new_number_count += 1
                    logger.info(f"Assigned new film number {film_number} to standard roll {roll_id}")
                
                # Update film_rolls structure with the assigned film number
                film_rolls["rolls"][roll_id]["film_number"] = film_number
                film_rolls["rolls"][roll_id]["film_number_source"] = "temp_roll" if temp_roll_id else "new"
                
                if temp_roll_id:
                    film_rolls["rolls"][roll_id]["source_temp_roll"] = source_temp_roll
                
                # Get rollInfo data if available
                if source_temp_roll:
                    film_rolls["rolls"][roll_id]["rollInfo"] = {
                        "source": "temp_roll",
                        "temp_roll_id": temp_roll_id,
                    }
                else:
                    film_rolls["rolls"][roll_id]["rollInfo"] = {
                        "source": "new",
                    }
                
                # Add to database
                if temp_roll_id is None:
                    cursor.execute(
                        "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            film_number,
                            "16mm",
                            roll_data.get("pages", CAPACITY_16MM),
                            roll_data.get("pagesUsed", 0),
                            roll_data.get("pagesRemaining", 0),
                            "active",
                            project_id,
                            roll_data.get("creation_date", datetime.now().isoformat())
                        )
                    )
                    roll_db_id = cursor.lastrowid
                
                # Add documents to Documents table
                if "documents" in roll_data:
                    # Sort documents by their document_index to ensure they are added in correct order
                    sorted_documents = sorted(roll_data["documents"].items(), 
                                           key=lambda x: x[1].get("document_index", 0))
                    
                    for doc_name, doc_data in sorted_documents:
                        blip_str = generate_blip(film_number, doc_data.get("document_index", 0), doc_data.get("frameRange", [0, 0])[0]) 
                        page_range = doc_data.get("pagerange", [0, 0])
                        cursor.execute("""
                            INSERT INTO Documents (document_name, com_id, roll_id, page_range_start, page_range_end, is_oversized, filepath, blip)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            doc_name,
                            doc_data.get("com_id", ""),  # Add this line to include com_id
                            roll_db_id,
                            page_range[0],
                            page_range[1],
                            doc_data.get("hasOversized", False),
                            doc_data.get("path", ""),
                            blip_str
                        ))
                
                # If this roll is partial and has enough remaining capacity, create a temp roll
                if is_partial and temp_roll_id is None and roll_data.get("partialRollInfo"):
                    usable_capacity = roll_data["partialRollInfo"].get("usableCapacity", 0)
                    
                    if usable_capacity >= TEMP_ROLL_MIN_USABLE_PAGES:
                        # Create a temp roll
                        cursor.execute(
                            "INSERT INTO TempRolls (film_type, capacity, usable_capacity, status, creation_date, source_roll_id, chain_film_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (
                                "16mm",
                                roll_data["partialRollInfo"].get("remainingCapacity", 0),
                                usable_capacity,
                                "available",
                                datetime.now().isoformat(),
                                roll_db_id,
                                film_number  # Set the chain_film_number to continue with this film number
                            )
                        )
                        temp_roll_id = cursor.lastrowid
                        created_temp_roll_count += 1
                        
                        # Update roll with created temp roll ID
                        cursor.execute(
                            "UPDATE Rolls SET created_temp_roll_id = ? WHERE roll_id = ?",
                            (temp_roll_id, roll_db_id)
                        )
                        
                        # Update film_rolls structure
                        film_rolls["rolls"][roll_id]["created_temp_roll_id"] = temp_roll_id
                        logger.success(f"Created temp roll {temp_roll_id} from partial roll {roll_id} with {usable_capacity} usable capacity")
                
                processed_count += 1
            
            logger.success(f"Processed {processed_count} standard rolls, assigned {assigned_new_number_count} new film numbers")
            if used_temp_roll_count > 0:
                logger.info(f"Used {used_temp_roll_count} temp rolls")
            if created_temp_roll_count > 0:
                logger.info(f"Created {created_temp_roll_count} new temp rolls")
        
        # Commit transaction
        commit_transaction(conn)
        logger.success(f"Committed database transaction")
        
    except Exception as e:
        rollback_transaction(conn)
        logger.error(f"Error assigning film numbers: {e}")
        logger.warning(f"Database transaction rolled back")
        raise
    finally:
        # Always close the connection
        close_connection(conn)
        logger.debug(f"Closed database connection")
    
    logger.success(f"Film number assignment completed successfully")
    return film_rolls

def process_16mm_rolls(cursor: sqlite3.Cursor, film_rolls: Dict[str, Any], project_id: int) -> Dict[str, Any]:
    """
    Process all 16mm rolls for film number assignment.
    
    Args:
        cursor: Database cursor
        film_rolls: The film_rolls data structure
        project_id: ID of the project
        
    Returns:
        dict: Updated film_rolls
    """
    if "16mm" not in film_rolls or not film_rolls["16mm"]["rolls"]:
        logger.info(f"No 16mm rolls found to process")
        return film_rolls
    
    # Get statistics
    total_rolls = len(film_rolls["16mm"]["rolls"])
    full_rolls = total_rolls - film_rolls["16mm"]["statistics"]["total_partial_rolls"]
    partial_rolls = film_rolls["16mm"]["statistics"]["total_partial_rolls"]
    
    logger.info(f"Processing {total_rolls} 16mm rolls ({full_rolls} full, {partial_rolls} partial)")
    
    processed_count = 0
    assigned_new_number_count = 0
    used_temp_roll_count = 0
    created_temp_roll_count = 0
    
    # Process each 16mm roll
    for roll_id, roll_data in film_rolls["16mm"]["rolls"].items():
        if not roll_id.isdigit():
            logger.debug(f"Skipping non-numeric roll ID: {roll_id}")
            continue
            
        # Check if film number already assigned
        if roll_data.get("film_number") is not None:
            logger.debug(f"Roll {roll_id} already has film number {roll_data['film_number']}, skipping")
            continue
        
        logger.info(f"Processing 16mm roll {roll_id}")
        if roll_data.get("isPartial", False):
            logger.debug(f"Roll {roll_id} is a partial roll with {roll_data.get('pagesUsed', 0)} pages used")
        else:
            logger.debug(f"Roll {roll_id} is a full roll with {roll_data.get('pagesUsed', 0)} pages used")
        
        # Calculate pages needed
        pages_needed = roll_data.get("pagesUsed", 0)
        logger.debug(f"Roll {roll_id} requires {pages_needed} pages")
        
        # Check if this is a partial roll that could use a temp roll
        is_partial = roll_data.get("isPartial", False)
        film_number = None
        temp_roll_id = None
        source_temp_roll = None
        
        if is_partial:
            logger.info(f"Checking for temp rolls for partial roll {roll_id}")
            # Try to find a suitable temp roll
            temp_roll_result = find_suitable_temp_roll(cursor, pages_needed, "16mm")
            
            if temp_roll_result:
                temp_roll_id, source_roll_id, usable_capacity = temp_roll_result
                
                logger.success(f"Found suitable temp roll {temp_roll_id} with {usable_capacity} capacity")
                
                # Always generate a new film number based on the current project location
                location = get_project_location(cursor, project_id)
                film_number = get_next_film_number(cursor, location)
                
                logger.info(f"Using temp roll {temp_roll_id} with {usable_capacity} capacity for partial 16mm roll {roll_id}")
                
                # Calculate remaining capacity after use
                remaining_capacity = usable_capacity - pages_needed
                logger.debug(f"After use: remaining capacity = {remaining_capacity}")
                
                # Format for logging
                source_temp_roll = f"temp_roll_{temp_roll_id}"
                used_temp_roll_count += 1
                
                # If there's enough remaining capacity, create a new temp roll from the remainder
                if remaining_capacity >= TEMP_ROLL_MIN_USABLE_PAGES:
                    logger.info(f"Enough remaining capacity to create new temp roll: {remaining_capacity} >= {TEMP_ROLL_MIN_USABLE_PAGES}")
                    # Calculate usable capacity (apply any required padding)
                    usable_remainder = remaining_capacity - TEMP_ROLL_PADDING_16MM
                    logger.debug(f"Applied padding: remaining_capacity={remaining_capacity}, usable_remainder={usable_remainder}")
                    
                    # Check if usable remainder is still enough after padding
                    if usable_remainder < TEMP_ROLL_MIN_USABLE_PAGES:
                        logger.warning(f"Not enough remaining capacity after padding: {usable_remainder} < {TEMP_ROLL_MIN_USABLE_PAGES}")
                        # Use the temp roll without creating a new one
                        cursor.execute(
                            "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date, source_temp_roll_id, film_number_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                film_number,
                                "16mm",
                                usable_capacity,
                                pages_needed,
                                0,
                                "active",
                                project_id,
                                roll_data.get("creation_date", datetime.now().isoformat()),
                                temp_roll_id,
                                "temp_roll"
                            )
                        )
                        roll_db_id = cursor.lastrowid
                        logger.debug(f"Created roll record in database with ID {roll_db_id}")
                        
                        # Mark the temp roll as used
                        mark_temp_roll_used(cursor, temp_roll_id, roll_db_id)
                        logger.debug(f"Marked temp roll {temp_roll_id} as used by roll {roll_db_id}")
                        
                        logger.info(f"Used entire temp roll {temp_roll_id} for partial 16mm roll {roll_id} (not enough usable capacity after padding)")
                        continue
                    
                    # Insert roll first to get its ID
                    cursor.execute(
                        "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date, source_temp_roll_id, film_number_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            film_number,
                            "16mm",
                            usable_capacity,
                            pages_needed,
                            0,
                            "active",
                            project_id,
                            roll_data.get("creation_date", datetime.now().isoformat()),
                            temp_roll_id,
                            "temp_roll"
                        )
                    )
                    roll_db_id = cursor.lastrowid
                    logger.debug(f"Created roll record in database with ID {roll_db_id}")
                    
                    # Mark the temp roll as used
                    mark_temp_roll_used(cursor, temp_roll_id, roll_db_id)
                    logger.debug(f"Marked temp roll {temp_roll_id} as used by roll {roll_db_id}")
                    
                    # Create a new temp roll from the remainder
                    new_temp_roll_id = create_temp_roll_from_remainder(
                        cursor, 
                        temp_roll_id, 
                        remaining_capacity, 
                        usable_remainder,
                        roll_db_id
                    )
                    
                    if new_temp_roll_id:
                        logger.success(f"Created new temp roll {new_temp_roll_id} from remainder with {usable_remainder} usable capacity")
                        created_temp_roll_count += 1
                        
                        # Update roll with created temp roll ID
                        cursor.execute(
                            "UPDATE Rolls SET created_temp_roll_id = ? WHERE roll_id = ?",
                            (new_temp_roll_id, roll_db_id)
                        )
                        logger.debug(f"Updated roll {roll_db_id} with created temp roll ID {new_temp_roll_id}")
                        
                        # Update film_rolls structure
                        film_rolls["16mm"]["rolls"][roll_id]["created_temp_roll_id"] = new_temp_roll_id
                        logger.debug(f"Updated film_rolls structure with created_temp_roll_id {new_temp_roll_id}")
                else:
                    logger.warning(f"Not enough remaining capacity for new temp roll: {remaining_capacity} < {TEMP_ROLL_MIN_USABLE_PAGES}")
                    # Just use the temp roll without creating a new one from remainder
                    cursor.execute(
                        "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date, source_temp_roll_id, film_number_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            film_number,
                            "16mm",
                            usable_capacity,
                            pages_needed,
                            0,
                            "active",
                            project_id,
                            roll_data.get("creation_date", datetime.now().isoformat()),
                            temp_roll_id,
                            "temp_roll"
                        )
                    )
                    roll_db_id = cursor.lastrowid
                    logger.debug(f"Created roll record in database with ID {roll_db_id}")
                    
                    # Mark the temp roll as used
                    mark_temp_roll_used(cursor, temp_roll_id, roll_db_id)
                    logger.debug(f"Marked temp roll {temp_roll_id} as used by roll {roll_db_id}")
                    
                    logger.info(f"Used entire temp roll {temp_roll_id} for partial 16mm roll {roll_id}")
            else:
                logger.info(f"No suitable temp roll found, assigning new film number")
                # No suitable temp roll found, assign a new film number
                location = get_project_location(cursor, project_id)
                film_number = get_next_film_number(cursor, location)
                assigned_new_number_count += 1
                logger.info(f"Assigned new film number {film_number} to partial 16mm roll {roll_id} (no suitable temp roll)")
        else:
            # Full roll, assign a new film number
            location = get_project_location(cursor, project_id)
            film_number = get_next_film_number(cursor, location)
            assigned_new_number_count += 1
            logger.info(f"Assigned film number {film_number} to full 16mm roll {roll_id}")
        
        # Assign film number to roll in film_rolls structure
        film_rolls["16mm"]["rolls"][roll_id]["film_number"] = film_number
        logger.debug(f"Updated film_rolls structure with film number {film_number} for roll {roll_id}")
        
        if source_temp_roll:
            film_rolls["16mm"]["rolls"][roll_id]["source_temp_roll"] = source_temp_roll
            logger.debug(f"Added source_temp_roll: {source_temp_roll} to roll {roll_id}")
        
        # If we haven't inserted the roll record yet (when not using a temp roll)
        if temp_roll_id is None:
            # Add to Rolls table
            cursor.execute(
                "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    film_number,
                    "16mm",
                    roll_data.get("pages", CAPACITY_16MM),
                    roll_data.get("pagesUsed", 0),
                    roll_data.get("pagesRemaining", 0),
                    "active",
                    project_id,
                    roll_data.get("creation_date", datetime.now().isoformat())
                )
            )
            roll_db_id = cursor.lastrowid
            logger.debug(f"Created roll record in database with ID {roll_db_id}")
        
        # Add documents to Documents table
        if "documents" in roll_data:
            logger.info(f"Adding {len(roll_data['documents'])} documents to Documents table for roll {roll_id}")
            
            for doc_name, doc_data in roll_data["documents"].items():
                page_start, page_end = doc_data["pagerange"]
                frame_start, frame_end = doc_data["frameRange"]

                # Retrieve or default the "document_index" (like update_index_data does)
                doc_index = doc_data.get("document_index", 1)  # fallback to 1 if missing
                
                # Construct the blip string in the same format as update_index_data:
                # "film_number-{doc_index:04d}.{page_start:05d}"
                #blip_str = f"{film_number}-{doc_index:04d}.{frame_start:05d}"
                
                #logger.debug(f"Adding document {doc_name} with frames {frame_start}-{frame_end}, "
                #             f"blip={blip_str}, to roll_id={roll_db_id}")
                
                # Insert into the DB with the new blip column
                cursor.execute("""
                    INSERT INTO Documents (
                        document_name, com_id, roll_id, 
                        page_range_start, page_range_end, 
                        is_oversized, filepath, blip
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_name,
                    doc_data.get("com_id", ""),
                    roll_db_id,
                    page_start,
                    page_end,
                    doc_data.get("hasOversized", False),
                    doc_data.get("path", ""),
                    doc_data.get("blip", "")
                ))
                
                # Also store the blip in film_rolls in-memory dict
                film_rolls["16mm"]["rolls"][roll_id]["documents"][doc_name]["blip"] = doc_data.get("blip", "")
        
        # If partial roll with enough capacity, create temp roll
        if is_partial and roll_data.get("partialRollInfo") and temp_roll_id is None:
            usable_capacity = roll_data["partialRollInfo"].get("usableCapacity", 0)
            
            logger.info(f"Checking if partial roll {roll_id} has enough capacity to create temp roll: {usable_capacity}")
            
            if usable_capacity >= TEMP_ROLL_MIN_USABLE_PAGES:
                logger.info(f"Enough capacity to create temp roll: {usable_capacity} >= {TEMP_ROLL_MIN_USABLE_PAGES}")
                # Create a temp roll
                new_temp_roll_id = create_temp_roll(
                    cursor,
                    "16mm",
                    roll_data["partialRollInfo"].get("remainingCapacity", 0),
                    usable_capacity,
                    roll_db_id,
                )
                
                if new_temp_roll_id:
                    logger.success(f"Created temp roll {new_temp_roll_id} from partial 16mm roll {roll_id} with {usable_capacity} usable capacity")
                    created_temp_roll_count += 1
                    
                    # Update roll with temp roll ID
                    cursor.execute(
                        "UPDATE Rolls SET created_temp_roll_id = ? WHERE roll_id = ?",
                        (new_temp_roll_id, roll_db_id)
                    )
                    logger.debug(f"Updated roll {roll_db_id} with created temp roll ID {new_temp_roll_id}")
                    
                    # Update film_rolls structure
                    film_rolls["16mm"]["rolls"][roll_id]["temp_roll_id"] = new_temp_roll_id
                    logger.debug(f"Updated film_rolls structure with temp_roll_id {new_temp_roll_id} for roll {roll_id}")
                else:
                    logger.warning(f"Failed to create temp roll from roll {roll_id}")
            else:
                logger.warning(f"Not enough capacity to create temp roll: {usable_capacity} < {TEMP_ROLL_MIN_USABLE_PAGES}")
        
        processed_count += 1
    
    # Log summary
    logger.success(f"Processed {processed_count} 16mm rolls:")
    logger.success(f"  - Assigned {assigned_new_number_count} new film numbers")
    logger.success(f"  - Used {used_temp_roll_count} temp rolls")
    logger.success(f"  - Created {created_temp_roll_count} new temp rolls")
    
    return film_rolls

def process_35mm_rolls(cursor: sqlite3.Cursor, film_rolls: Dict[str, Any], project_id: int) -> Dict[str, Any]:
    """
    Process all 35mm rolls for film number assignment.
    
    Args:
        cursor: Database cursor
        film_rolls: The film_rolls data structure
        project_id: ID of the project
        
    Returns:
        dict: Updated film_rolls
    """
    if "35mm" not in film_rolls or not film_rolls["35mm"]["rolls"]:
        logger.info(f"No 35mm rolls found to process")
        return film_rolls
    
    # Get statistics
    total_rolls = len(film_rolls["35mm"]["rolls"])
    full_rolls = total_rolls - film_rolls["35mm"]["statistics"]["total_partial_rolls"]
    partial_rolls = film_rolls["35mm"]["statistics"]["total_partial_rolls"]
    
    logger.info(f"Processing {total_rolls} 35mm rolls ({full_rolls} full, {partial_rolls} partial)")
    
    processed_count = 0
    assigned_new_number_count = 0
    used_active_35mm_count = 0
    created_temp_roll_count = 0
    
    # Get the project location to ensure location consistency when reusing rolls
    location = get_project_location(cursor, project_id)
    logger.debug(f"Project location: {location}")
    
    # First, look for an active 35mm roll that has capacity
    active_35mm_roll = None
    active_35mm_film_number = None
    
    # Process each 35mm roll
    for roll_id, roll_data in film_rolls["35mm"]["rolls"].items():
        if not roll_id.isdigit():
            logger.debug(f"Skipping non-numeric roll ID: {roll_id}")
            continue
            
        # Check if film number already assigned
        if roll_data.get("film_number") is not None:
            logger.debug(f"Roll {roll_id} already has film number {roll_data['film_number']}, skipping")
            continue
        
        logger.info(f"Processing 35mm roll {roll_id}")
        
        # Calculate pages needed
        pages_needed = roll_data.get("pagesUsed", 0)
        logger.debug(f"Roll {roll_id} requires {pages_needed} pages")
        
        # Try to find an active 35mm roll with capacity, ensuring location consistency
        active_roll = find_active_35mm_roll(cursor, pages_needed, location)
        
        if active_roll:
            roll_db_id, film_number, remaining_capacity = active_roll
            logger.success(f"Found active 35mm roll with ID {roll_db_id}, film number {film_number}, and {remaining_capacity} remaining capacity")
            
            # Use this film number
            film_rolls["35mm"]["rolls"][roll_id]["film_number"] = film_number
            film_rolls["35mm"]["rolls"][roll_id]["film_number_source"] = "active_35mm"
            film_rolls["35mm"]["rolls"][roll_id]["source_roll_id"] = roll_db_id
            
            # Add rollInfo data
            film_rolls["35mm"]["rolls"][roll_id]["rollInfo"] = {
                "source": "active_35mm",
                "roll_id": roll_db_id,
                "remaining_before": remaining_capacity,
                "remaining_after": remaining_capacity - pages_needed
            }
            
            # Update the active roll usage
            update_35mm_roll_usage(cursor, roll_db_id, pages_needed)
            logger.debug(f"Updated active 35mm roll {roll_db_id} with {pages_needed} pages used")
            
            used_active_35mm_count += 1
            
            # Add documents to Documents table
            if "documents" in roll_data:
                # Sort documents by their document_index to ensure they are added in correct order
                sorted_documents = sorted(roll_data["documents"].items(), 
                                       key=lambda x: x[1].get("document_index", 0))
                
                for doc_name, doc_data in sorted_documents:
                    page_range = doc_data.get("pagerange", [0, 0])
                    cursor.execute("""
                        INSERT INTO Documents (document_name, com_id, roll_id, page_range_start, page_range_end, is_oversized, filepath)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        doc_name,
                        doc_data.get("com_id", ""),  # Add this line to include com_id
                        roll_db_id,
                        page_range[0],
                        page_range[1],
                        doc_data.get("hasOversized", True),  # 35mm documents are likely oversized
                        doc_data.get("path", "")
                    ))
        else:
            # No active roll found, get a new film number
            location = get_project_location(cursor, project_id)
            film_number = get_next_film_number(cursor, location)
            logger.info(f"Assigned new film number {film_number} to 35mm roll {roll_id}")
            
            # Assign to roll
            film_rolls["35mm"]["rolls"][roll_id]["film_number"] = film_number
            film_rolls["35mm"]["rolls"][roll_id]["film_number_source"] = "new"
            
            # Add rollInfo data
            film_rolls["35mm"]["rolls"][roll_id]["rollInfo"] = {
                "source": "new"
            }
            
            # Add to database
            cursor.execute(
                "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, pages_remaining, status, project_id, creation_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    film_number,
                    "35mm",
                    roll_data.get("pages", CAPACITY_35MM),
                    roll_data.get("pagesUsed", 0),
                    roll_data.get("pagesRemaining", 0),
                    "active",
                    project_id,
                    roll_data.get("creation_date", datetime.now().isoformat())
                )
            )
            roll_db_id = cursor.lastrowid
            logger.debug(f"Created 35mm roll record in database with ID {roll_db_id}")
            
            # Add documents to Documents table
            if "documents" in roll_data:
                # Sort documents by their document_index to ensure they are added in correct order
                sorted_documents = sorted(roll_data["documents"].items(), 
                                       key=lambda x: x[1].get("document_index", 0))
                
                for doc_name, doc_data in sorted_documents:
                    page_range = doc_data.get("pagerange", [0, 0])
                    cursor.execute("""
                        INSERT INTO Documents (document_name, com_id, roll_id, page_range_start, page_range_end, is_oversized, filepath)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        doc_name,
                        doc_data.get("com_id", ""),  # Add this line to include com_id
                        roll_db_id,
                        page_range[0],
                        page_range[1],
                        doc_data.get("hasOversized", True),  # 35mm documents are likely oversized
                        doc_data.get("path", "")
                    ))
            
            assigned_new_number_count += 1
        
        processed_count += 1
    
    logger.success(f"Processed {processed_count} 35mm rolls, assigned {assigned_new_number_count} new film numbers")
    if used_active_35mm_count > 0:
        logger.info(f"Used {used_active_35mm_count} active 35mm rolls")
    
    return film_rolls

def update_index_data(index_data: Dict[str, Any], film_rolls: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update index data with film numbers from film_rolls.
    Only processes 16mm rolls (35mm rolls are intentionally excluded).
    
    Args:
        index_data: Dictionary containing index data
        film_rolls: Dictionary containing film rolls with film numbers
        
    Returns:
        dict: Updated index data
    """
    logger.info(f"Updating index with film numbers")
    
    if not index_data or "index" not in index_data:
        logger.error(f"Invalid index data structure")
        return index_data
    
    # Create dictionaries to map roll_id to film_number and source information
    roll_film_numbers = {}  # {roll_id: film_number}
    roll_sources = {}       # {roll_id: source_info}
    
    # Extract 16mm film numbers (for projects with oversized pages)
    if "16mm" in film_rolls:
        logger.debug(f"Processing 16mm roll film numbers")
        for roll_id, roll_data in film_rolls["16mm"]["rolls"].items():
            if "film_number" in roll_data and roll_data["film_number"]:
                roll_film_numbers[roll_id] = roll_data["film_number"]
                # Check if this roll has a source (temp roll or shared)
                if "source_temp_roll" in roll_data:
                    roll_sources[roll_id] = roll_data["source_temp_roll"]
                    logger.debug(f"Found 16mm roll {roll_id} with film number {roll_data['film_number']} from temp roll")
                elif "source_roll" in roll_data:
                    roll_sources[roll_id] = roll_data["source_roll"]
                    logger.debug(f"Found 16mm roll {roll_id} with film number {roll_data['film_number']} from shared roll")
                else:
                    logger.debug(f"Found 16mm roll {roll_id} with film number {roll_data['film_number']} (direct assignment)")
    
    # Note: 35mm rolls are intentionally excluded from index processing
    
    # Extract standard roll film numbers (for projects without oversized pages)
    elif "rolls" in film_rolls:
        logger.debug(f"Processing standard roll film numbers")
        for roll_id, roll_data in film_rolls["rolls"].items():
            if "film_number" in roll_data and roll_data["film_number"]:
                roll_film_numbers[roll_id] = roll_data["film_number"]
                # Check if this roll has a source (temp roll or shared)
                if "source_temp_roll" in roll_data:
                    roll_sources[roll_id] = roll_data["source_temp_roll"]
                    logger.debug(f"Found standard roll {roll_id} with film number {roll_data['film_number']} from temp roll")
                elif "source_roll" in roll_data:
                    roll_sources[roll_id] = roll_data["source_roll"]
                    logger.debug(f"Found standard roll {roll_id} with film number {roll_data['film_number']} from shared roll")
                else:
                    logger.debug(f"Found standard roll {roll_id} with film number {roll_data['film_number']} (direct assignment)")
    
    logger.debug(f"Created lookup dictionaries with {len(roll_film_numbers)} film numbers and {len(roll_sources)} sources")
                    
    # Update each index entry
    updated_count = 0
    missing_count = 0
    
    for entry_idx, entry in enumerate(index_data["index"]):
        # Get roll_id and frame range from initial_index
        # Format: [roll_id, frame_start, frame_end]
        if len(entry) >= 4 and entry[2]:
            roll_id, frame_start, frame_end = entry[2]
            roll_id_str = str(roll_id)
            
            # Get document index (use 5th element if available, default to 1)
            doc_index = entry[4] if len(entry) >= 5 else 1
            
            #logger.debug(f"Processing index entry {entry_idx+1}: document {entry[0]}, roll {roll_id_str}, frames {frame_start}-{frame_end}, doc_index {doc_index}")
            
            # Find corresponding film_number in roll_film_numbers
            if roll_id_str in roll_film_numbers:
                film_number = roll_film_numbers[roll_id_str]
                source_info = roll_sources.get(roll_id_str, "direct")
                
                # Update the final_index
                if film_number:
                    # Use new format: film_number-document_index(4 digits)-frame_start(5 digits)
                    entry[3] = f"{film_number}-{doc_index:04d}.{frame_start:05d}"
                    updated_count += 1
                    
                    # Add detailed source information for debugging
                    #if source_info != "direct":
                    #    logger.debug(f"Updated index for document {entry[0]}: {entry[3]} (source: {source_info})")
                    #else:
                    #    logger.debug(f"Updated index for document {entry[0]}: {
                    #        entry[3]}")
                else:
                    logger.warning(f"Warning: No film number found for roll {roll_id_str} containing document {entry[0]}")
                    missing_count += 1
            else:
                logger.warning(f"Warning: Roll {roll_id_str} not found in film_rolls for document {entry[0]}")
                missing_count += 1
    
    logger.success(f"Successfully updated {updated_count} index entries with film numbers")
    if missing_count > 0:
        logger.warning(f"Could not update {missing_count} index entries due to missing film numbers")
    
    return index_data


# --------------------------------  ACTIVE AND TEMP ROLL UTILITIES -------------------------------

def get_next_film_number(cursor: sqlite3.Cursor, location: str = "OU") -> str:
    """
    Get the next available film number based on location.
    
    Args:
        cursor: Database cursor
        location: Location code (e.g., "OU" or "DW")
        
    Returns:
        str: Next available film number (format: 10000001 for OU, 20000001 for DW)
    """
    # Determine prefix based on location
    prefix = "1" if location == "OU" else "2" if location == "DW" else "3"
    
    # Query for the highest film number with the same prefix AND from the same location
    cursor.execute("""
        SELECT r.film_number 
        FROM Rolls r
        JOIN Projects p ON r.project_id = p.project_id
        WHERE r.film_number LIKE ?||'%' AND p.location = ?
        ORDER BY r.film_number DESC 
        LIMIT 1
    """, (prefix, location))
    
    result = cursor.fetchone()
    
    if result is None:
        # No film numbers for this prefix yet, start with base number
        base_number = f"{prefix}0000001"
        return base_number
    
    # Extract the number part and increment
    last_number = result[0]
    match = re.match(r'(\d{8})', last_number)
    if match:
        number = int(match.group(1)) + 1
        return f"{number:08d}"
    else:
        # Fallback if format is unexpected
        base_number = f"{prefix}0000001"
        return base_number

def find_suitable_temp_roll(cursor: sqlite3.Cursor, pages_needed: int, film_type: str = "16mm") -> Optional[Tuple[int, int, int]]:
    """
    Find a suitable temp roll for the given requirements, treating rolls as simple capacity containers.
    
    Args:
        cursor: Database cursor
        pages_needed: Number of pages needed
        film_type: Type of film (16mm or 35mm)
        
    Returns:
        Optional tuple: (temp_roll_id, source_roll_id, usable_capacity) or None if no suitable roll
    """
    logger.info(f"Looking for temp roll: film_type={film_type}, pages_needed={pages_needed}")
    
    # Simply find any available temp roll with sufficient capacity
    cursor.execute("""
        SELECT temp_roll_id, source_roll_id, usable_capacity
        FROM TempRolls 
        WHERE film_type = ? 
        AND status = 'available' 
        AND usable_capacity >= ? 
        ORDER BY usable_capacity ASC
        LIMIT 1
    """, (film_type, pages_needed))
    
    result = cursor.fetchone()
    if result:
        logger.success(f"Found suitable temp roll {result[0]} with {result[2]} capacity")
    else:
        logger.error(f"No suitable temp roll found")
    
    return result

def create_temp_roll(cursor: sqlite3.Cursor, film_type: str, capacity: int, 
                   usable_capacity: int, source_roll_id: int) -> int:
    """
    Create a new temp roll entry in the database.
    
    Args:
        cursor: Database cursor
        film_type: Type of film (16mm or 35mm)
        capacity: Total capacity of the temp roll
        usable_capacity: Usable capacity after padding
        source_roll_id: ID of the roll that created this temp roll
        
    Returns:
        int: ID of the newly created temp roll
    """
    logger.info(f"Creating new temp roll: type={film_type}, capacity={capacity}, usable={usable_capacity}, source_roll={source_roll_id}")
    
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO TempRolls (
            film_type, capacity, usable_capacity, status,
            creation_date, source_roll_id
        ) VALUES (?, ?, ?, 'available', ?, ?)
    """, (film_type, capacity, usable_capacity, creation_date, source_roll_id))
    
    temp_roll_id = cursor.lastrowid
    logger.success(f"Created temp roll with ID: {temp_roll_id}")
    
    return temp_roll_id

def mark_temp_roll_used(cursor: sqlite3.Cursor, temp_roll_id: int, used_by_roll_id: int) -> None:
    """
    Mark a temp roll as used.
    
    Args:
        cursor: Database cursor
        temp_roll_id: ID of the temp roll
        used_by_roll_id: ID of the roll that used this temp roll
    """
    logger.info(f"Marking temp roll {temp_roll_id} as used by roll {used_by_roll_id}")
    
    # Get temp roll details before updating
    cursor.execute("""
        SELECT film_type, usable_capacity, chain_film_number, parent_temp_roll_id, child_temp_roll_id
        FROM TempRolls
        WHERE temp_roll_id = ?
    """, (temp_roll_id,))
    
    result = cursor.fetchone()
    if result:
        film_type, usable_capacity, chain_film_number, parent_temp_roll_id, child_temp_roll_id = result
        logger.debug(f"Temp Roll {temp_roll_id}: type={film_type}, capacity={usable_capacity}, chain={chain_film_number}")
        logger.debug(f"Relations: parent={parent_temp_roll_id}, child={child_temp_roll_id}")
    
    cursor.execute("""
        UPDATE TempRolls 
        SET status = 'used', used_by_roll_id = ? 
        WHERE temp_roll_id = ?
    """, (used_by_roll_id, temp_roll_id))
    
    logger.success(f"Temp roll {temp_roll_id} marked as used")

def get_temp_roll_film_number(cursor: sqlite3.Cursor, project_id: int) -> str:
    """
    Generate a new film number for a project based on its location.
    
    Args:
        cursor: Database cursor
        project_id: ID of the project
        
    Returns:
        str: New film number to use
    """
    location = get_project_location(cursor, project_id)
    film_number = get_next_film_number(cursor, location)
    logger.success(f"Generated new film number: {film_number} for location: {location}")
    return film_number

def create_temp_roll_from_remainder(cursor: sqlite3.Cursor, used_temp_roll_id: int, 
                                  remainder_capacity: int, usable_remainder: int,
                                  roll_id: int) -> Optional[int]:
    """
    Create a new temp roll from the remainder of a used temp roll.
    
    Args:
        cursor: Database cursor
        used_temp_roll_id: ID of the temp roll that was used
        remainder_capacity: Remaining capacity after use
        usable_remainder: Usable remainder after padding
        roll_id: ID of the roll that used the temp roll
        
    Returns:
        Optional[int]: ID of the newly created temp roll, or None if not enough capacity
    """
    logger.info(f"Creating temp roll from remainder of temp roll {used_temp_roll_id}")
    logger.debug(f"Remainder: total={remainder_capacity}, usable={usable_remainder}")
    
    # Get information about the used temp roll
    cursor.execute("""
        SELECT film_type, parent_temp_roll_id
        FROM TempRolls
        WHERE temp_roll_id = ?
    """, (used_temp_roll_id,))
    
    result = cursor.fetchone()
    if not result:
        logger.error(f"Used temp roll {used_temp_roll_id} not found")
        return None
    
    film_type, parent_temp_roll_id = result
    logger.debug(f"Used temp roll info: type={film_type}, parent={parent_temp_roll_id}")
    
    # Calculate usable capacity with proper padding based on film type
    if film_type == "16mm":
        usable_remainder = remainder_capacity - TEMP_ROLL_PADDING_16MM
    else:  # 35mm
        usable_remainder = remainder_capacity - TEMP_ROLL_PADDING_35MM
    
    logger.debug(f"Applied padding: remainder_capacity={remainder_capacity}, usable_remainder={usable_remainder}")
    
    # Check if usable remainder is enough to create a new temp roll
    if usable_remainder < TEMP_ROLL_MIN_USABLE_PAGES:  # Minimum usable capacity
        logger.error(f"Remainder too small ({usable_remainder}) to create a new temp roll (min: {TEMP_ROLL_MIN_USABLE_PAGES})")
        return None
    
    # Create new temp roll without passing chain_film_number to ensure new film number will be used
    new_temp_roll_id = create_temp_roll(
        cursor, 
        film_type, 
        remainder_capacity, 
        usable_remainder, 
        roll_id,  # The current roll becomes the source
    )
    
    logger.success(f"Created new temp roll {new_temp_roll_id} from remainder")
    return new_temp_roll_id

def get_roll_film_number(cursor: sqlite3.Cursor, roll_id: int) -> Optional[str]:
    """
    Get the film number for a specific roll.
    
    Args:
        cursor: Database cursor
        roll_id: ID of the roll
        
    Returns:
        Optional[str]: Film number for the roll or None if not found
    """
    cursor.execute("SELECT film_number FROM Rolls WHERE roll_id = ?", (roll_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def find_active_35mm_roll(cursor: sqlite3.Cursor, pages_needed: int, location: str = None) -> Optional[Tuple[int, str, int]]:
    """
    Find an existing active 35mm roll with sufficient capacity.
    
    Args:
        cursor: Database cursor
        pages_needed: Number of pages needed
        location: Optional location code (e.g., "OU" or "DW") to ensure location consistency
        
    Returns:
        Optional tuple: (roll_id, film_number, pages_remaining) or None if no suitable roll
    """
    if location:
        # Include location check in the query to ensure rolls are only reused within the same location
        cursor.execute("""
            SELECT r.roll_id, r.film_number, r.pages_remaining 
            FROM Rolls r
            JOIN Projects p ON r.project_id = p.project_id
            WHERE r.film_type = '35mm' 
            AND r.status = 'active' 
            AND r.pages_remaining >= ?
            AND p.location = ?
            ORDER BY r.creation_date DESC
            LIMIT 1
        """, (pages_needed, location))
    else:
        # Original query without location check
        cursor.execute("""
            SELECT roll_id, film_number, pages_remaining 
            FROM Rolls 
            WHERE film_type = '35mm' 
            AND status = 'active' 
            AND pages_remaining >= ? 
            ORDER BY creation_date DESC
            LIMIT 1
        """, (pages_needed,))
    
    result = cursor.fetchone()
    return result if result else None

def update_35mm_roll_usage(cursor: sqlite3.Cursor, roll_id: int, pages_used: int) -> None:
    """
    Update an existing 35mm roll with additional usage.
    
    Args:
        cursor: Database cursor
        roll_id: ID of the roll
        pages_used: Number of pages to add to the roll's usage
    """
    cursor.execute("""
        UPDATE Rolls 
        SET pages_used = pages_used + ?, 
            pages_remaining = pages_remaining - ? 
        WHERE roll_id = ?
    """, (pages_used, pages_used, roll_id)) 

# --------------------------------  DATABASE UTILITIES  -------------------------------
"""
This section contains utilities for database operations including:

1. Database Initialization and Schema Management
   - Creating tables with appropriate schemas and constraints
   - Setting up foreign key relationships between tables
   - Database version tracking and migration support

2. Connection Management
   - Opening and closing database connections safely
   - Connection pooling for performance optimization
   - Transaction handling with commit and rollback support

3. Project and Roll Data Operations
   - CRUD operations for project metadata
   - Roll creation, updating, and status management
   - Document-to-roll mapping and relationship tracking

4. Film Number Allocation System
   - Location-based film number generation (OU: 1xxxx, DW: 2xxxx, Other: 3xxxx)
   - Sequential allocation with gap detection and prevention
   - Film number validation and uniqueness enforcement
   - Tracking of used and available film numbers across projects

5. Roll Capacity Management
   - 16mm rolls: 2900 pages capacity with 150 page padding
   - 35mm rolls: 690 pages capacity with 150 page padding
   - Minimum usable partial roll threshold of 100 pages
   - Remaining capacity calculation and tracking

6. Partial Roll Handling
   - Tracking remaining and usable capacity on partially used rolls
   - Location-aware roll reuse for 35mm film
   - Roll relationship tracking (parent/child relationships)
   - Creation date and usage history for audit purposes

7. Query Utilities
   - Specialized queries for film allocation statistics
   - Roll usage reporting and capacity analysis
   - Project status and progress tracking
   - Error detection and data consistency verification

8. Transaction Safety
   - Atomic operations for critical updates
   - Error recovery with automatic rollback
   - Integrity constraint enforcement
   - Concurrency control for multi-user access
"""


def init_database() -> None:
    """Initialize database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create Projects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Projects (
        project_id INTEGER PRIMARY KEY,
        archive_id TEXT NOT NULL, 
        location TEXT,
        doc_type TEXT,
        path TEXT,
        folderName TEXT,
        oversized BOOLEAN,
        total_pages INTEGER,
        total_pages_with_refs INTEGER,
        date_created TEXT,
        data_dir TEXT,
        index_path TEXT
    )
    """)
    
    # Create Rolls table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Rolls (
        roll_id INTEGER PRIMARY KEY,
        film_number TEXT,
        film_type TEXT,
        capacity INTEGER,
        pages_used INTEGER,
        pages_remaining INTEGER,
        status TEXT,
        project_id INTEGER,
        creation_date TEXT,
        source_temp_roll_id INTEGER NULL,
        created_temp_roll_id INTEGER NULL,
        film_number_source TEXT NULL,
        FOREIGN KEY (project_id) REFERENCES Projects(project_id),
        FOREIGN KEY (source_temp_roll_id) REFERENCES TempRolls(temp_roll_id),
        FOREIGN KEY (created_temp_roll_id) REFERENCES TempRolls(temp_roll_id)
    )
    """)
    
    # Create TempRolls table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS TempRolls (
        temp_roll_id INTEGER PRIMARY KEY,
        film_type TEXT,
        capacity INTEGER,
        usable_capacity INTEGER,
        status TEXT,
        creation_date TEXT,
        source_roll_id INTEGER,
        used_by_roll_id INTEGER NULL,
        parent_temp_roll_id INTEGER NULL,
        child_temp_roll_id INTEGER NULL,
        chain_film_number TEXT NULL,
        chain_position INTEGER NULL,
        FOREIGN KEY (source_roll_id) REFERENCES Rolls(roll_id),
        FOREIGN KEY (used_by_roll_id) REFERENCES Rolls(roll_id),
        FOREIGN KEY (parent_temp_roll_id) REFERENCES TempRolls(temp_roll_id),
        FOREIGN KEY (child_temp_roll_id) REFERENCES TempRolls(temp_roll_id)
    )
    """)
    
    # Create Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Documents (
        document_id INTEGER PRIMARY KEY,
        document_name TEXT,
        com_id TEXT,
        roll_id INTEGER,
        page_range_start INTEGER,
        page_range_end INTEGER,
        is_oversized BOOLEAN,
        filepath TEXT,
        blip TEXT,
        FOREIGN KEY (roll_id) REFERENCES Rolls(roll_id)
    )
    """)
    
    conn.commit()
    conn.close()

def get_connection() -> sqlite3.Connection:
    """Get a connection to the database."""
    # Create the directory if it doesn't exist
    db_dir = os.path.dirname(DB_FILE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    # Initialize database if it doesn't exist
    if not os.path.exists(DB_FILE):
        init_database()
        
    return sqlite3.connect(DB_FILE)

def close_connection(conn: sqlite3.Connection) -> None:
    """Close a database connection."""
    if conn:
        conn.close()

def begin_transaction(conn: sqlite3.Connection) -> None:
    """Begin a new transaction."""
    conn.execute("BEGIN TRANSACTION")

def commit_transaction(conn: sqlite3.Connection) -> None:
    """Commit a transaction."""
    conn.commit()

def rollback_transaction(conn: sqlite3.Connection) -> None:
    """Rollback a transaction."""
    conn.rollback()

def with_transaction(func):
    """Decorator to wrap a function in a transaction."""
    def wrapper(*args, **kwargs):
        conn = get_connection()
        try:
            begin_transaction(conn)
            result = func(conn, *args, **kwargs)
            commit_transaction(conn)
            return result
        except Exception as e:
            rollback_transaction(conn)
            raise e
        finally:
            close_connection(conn)
    return wrapper

def get_project_location(cursor: sqlite3.Cursor, project_id: int) -> str:
    """
    Get the location for a project.
    
    Args:
        cursor: Database cursor
        project_id: Project ID
        
    Returns:
        str: Location code (e.g., "OU" or "DW"), defaults to "OU" if not found
    """
    cursor.execute("SELECT location FROM Projects WHERE project_id = ?", (project_id,))
    result = cursor.fetchone()
    
    if result and result[0]:
        return result[0]
    else:
        logger.warning(f"No location found for project {project_id}, defaulting to 'OU'")
        return "OU"

# --------------------------------  DOCUMENT MANIPULATION AND PROCESSING  ----------------------
"""
We need to manipulate the documents for different purposes:


For projects with oversizes:
1. Create reference sheets by generating a PDF for each range of oversize pages per document with this data:

    - Filmnumber:   10000001...             (filmRolls > film_number)
    - Archive ID:   RRD017-2024             (documentPages > archiveId)
    - Blip:         10000001-0001.00001     see below
    - Doc-Type:     FAIR                    (projectInfo > doc_type)
    - Human ranges: 1 von 2                 (filmRolls > readable_pages)
    - Barcode:      1427007501013191        (the documents filename)

2. Save the reference sheets with the same name as the document in a temporary dir "references" to access later

2.1 Prepend the reference sheets before the page range of the original document and save as a new file with same filename under new temp dir (referenced)

3. Extract only oversize pages to a new document with the same filename under a new diff temp dir (oversized)

4. Prepend the reference sheets to the new document with oversizes to its page ranges in the new document.

5. Copy the files to directories based on its assigned filmnumber.

6. Split documents if necessary

7. Save the dir in the parent dir of the initial input folder

BLIP: The blip is the location of the reference sheet on the 35mm film. It is a string that contains the film number, the document index, and the frame start.
Currently we only track the blip on th 16mm film. We need to track blips for 35mm across projects.
Which means we need to store the blip in the database for each document under "blip". 

For projects with no oversizes:
1. Copy the files to directories based on its assigned filmnumber.
2. If a documents allocation is split across rolls, we need to split the document accordingly and copy it to the new roll directory.

"""
def create_reference_sheet(document_name: str, 
                         film_number: str,
                         archive_id: str,
                         blip: str,
                         doc_type: str,
                         human_ranges: str,
                         barcode: str) -> bytes:
    """
    Create a reference sheet PDF in memory.
    
    Args:
        document_name: Name of the document
        film_number: Film number from filmRolls
        archive_id: Archive ID from documentPages
        blip: Blip value from initIndex
        doc_type: Document type from projectInfo
        human_ranges: Human readable page ranges
        barcode: Document barcode (filename)
    
    Returns:
        bytes: The PDF file content in memory
        
    Raises:
        ValueError: If any required parameter is empty or None
    """
    # Validate inputs
    if not all([document_name, film_number, archive_id, blip, doc_type, human_ranges, barcode]):
        raise ValueError("All parameters must be non-empty strings")
    
    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Create the content
    elements = []
    styles = getSampleStyleSheet()
    
    # Add document information
    elements.append(Paragraph(f"Filmnumber: {film_number}", styles["Normal"]))
    elements.append(Paragraph(f"Archive ID: {archive_id}", styles["Normal"]))
    elements.append(Paragraph(f"Blip: {blip}", styles["Normal"]))
    elements.append(Paragraph(f"Doc-Type: {doc_type}", styles["Normal"]))
    elements.append(Paragraph(f"Human ranges: {human_ranges}", styles["Normal"]))
    elements.append(Paragraph(f"Barcode: {barcode}", styles["Normal"]))
    
    # Build the PDF
    doc.build(elements)

    # Get the PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def process_documents(project_info: Dict[str, Any], 
                     document_pages: Dict[str, Any], 
                     film_rolls: Dict[str, Any],
                     index_data: Optional[Dict[str, Any]] = None) -> None:
    """Process all documents and create reference sheets."""
    logger.info("Starting document processing")
    
    # Create output directory in the same folder as the input
    input_path = Path(next(iter(project_info.values()))["path"])
    output_dir = input_path.parent / ".output"
    project_info["output_dir"] = str(output_dir)
    
    # Create temp directory structure
    temp_dir = output_dir / "temp"
    references_dir = temp_dir / "references"
    oversizes_dir = temp_dir / "oversizes"
    referenced_dir = temp_dir / "referenced"
    
    # Create all directories
    for dir_path in [temp_dir, references_dir, oversizes_dir, referenced_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Filter for oversized documents only
    oversized_docs = {doc_name: doc_data for doc_name, doc_data in document_pages.items() 
                     if doc_data.get("oversized", False)}
    
    # Process each oversized document
    total_docs = len(oversized_docs)
    processed_docs = 0
    error_docs = 0
    
    if total_docs == 0:
        logger.info("No oversized documents found to process")
        return
        
    logger.info(f"Found {total_docs} oversized documents to process")
    
    for doc_name, doc_data in oversized_docs.items():
        try:
            # Get roll information
            film_type, roll_id = find_roll_for_document(doc_name, film_rolls)
            if not roll_id:
                logger.warning(f"No roll found for document {doc_name}")
                error_docs += 1
                continue
                
            # Get film number based on film type
            if film_type in film_rolls and 'rolls' in film_rolls[film_type]:
                roll_data = film_rolls[film_type]['rolls'].get(roll_id, {})
                film_number = roll_data.get('film_number')
            else:
                film_number = None
                
            if not film_number:
                logger.warning(f"No film number found for roll {roll_id} of type {film_type}")
                error_docs += 1
                continue
            
            # Get source path - try different possible keys
            source_path = None
            for path_key in ['source_path', 'path', 'file_path']:
                if path_key in doc_data:
                    source_path = Path(doc_data[path_key])
                    break
                    
            if not source_path:
                logger.error(f"No source path found for document {doc_name}. Available keys: {list(doc_data.keys())}")
                error_docs += 1
                continue
                
            if not source_path.exists():
                logger.error(f"Source path does not exist for document {doc_name}: {source_path}")
                error_docs += 1
                continue
            
            # Get blip from index data
            blip = None
            if index_data and 'index' in index_data:
                for entry in index_data['index']:
                    if entry[0] == doc_name:  # Match document name
                        blip = entry[3]  # Get blip from index entry
                        break
            
            if not blip:
                logger.warning(f"No blip found in index for document {doc_name}")
                error_docs += 1
                continue
        
            # Get document info from project_info
            project_data = next(iter(project_info.values()))
            
            # Get oversized ranges
            oversized_ranges = []
            
            # Try to get ranges from document_pages first
            if 'ranges' in doc_data:
                oversized_ranges = doc_data['ranges']
            # Fall back to film_rolls if not found in document_pages
            elif film_type in film_rolls and 'rolls' in film_rolls[film_type]:
                roll_data = film_rolls[film_type]['rolls'].get(roll_id, {})
                doc_in_roll = roll_data.get('documents', {}).get(doc_name, {})
                if 'oversized_ranges' in doc_in_roll:
                    oversized_ranges = doc_in_roll['oversized_ranges']
            
            if not oversized_ranges:
                logger.warning(f"No oversized ranges found for document {doc_name}")
                error_docs += 1
                continue
            
            # Get human ranges from readable_pages
            human_ranges = doc_data.get('readable_pages', [])
            if not human_ranges:
                logger.warning(f"No readable pages found for document {doc_name}")
                error_docs += 1
                continue
            
            # Create a reference sheet for each oversized range
            for i, (range_start, range_end) in enumerate(oversized_ranges):
                try:
                    # Create a unique name for this range
                    range_name = f"{doc_name}_range_{range_start}-{range_end}"
                    
                    # Validate required parameters
                    required_params = {
                        "document_name": doc_name,
                        "film_number": film_number,
                        "archive_id": project_data.get("archiveId", ""),
                        "blip": blip,
                        "doc_type": project_data.get("doc_type", ""),
                        "human_ranges": human_ranges[i] if i < len(human_ranges) else human_ranges[0],
                        "barcode": doc_name
                    }
                    
                    # Check for empty parameters
                    empty_params = [k for k, v in required_params.items() if not v]
                    if empty_params:
                        raise ValueError(f"Missing required parameters: {', '.join(empty_params)}")
                    
                    reference_sheet = create_reference_sheet(
                        document_name=required_params["document_name"],
                        film_number=required_params["film_number"],
                        archive_id=required_params["archive_id"],
                        blip=required_params["blip"],
                        doc_type=required_params["doc_type"],
                        human_ranges=required_params["human_ranges"],
                        barcode=required_params["barcode"]
                    )
                    
                    # Save reference sheet in references directory
                    ref_sheet_path = references_dir / f"{range_name}_reference.pdf"
                    with open(ref_sheet_path, "wb") as f:
                        f.write(reference_sheet)
                        
                except Exception as e:
                    logger.error(f"Error creating reference sheet for {doc_name} range {range_start}-{range_end}: {str(e)}")
                    error_docs += 1
                    continue
            
            processed_docs += 1
            
            # Log progress every 10 documents
            if processed_docs % 10 == 0:
                logger.info(f"Processed {processed_docs}/{total_docs} documents")
                
        except Exception as e:
            logger.error(f"Error processing document {doc_name}: {str(e)}")
            error_docs += 1
            continue
    
    # Log final statistics
    logger.info(f"Document processing completed: {processed_docs} successful, {error_docs} failed out of {total_docs} total")
    if error_docs > 0:
        logger.warning(f"Some documents failed processing. Check logs for details.")

def find_roll_for_document(doc_name: str, film_rolls: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Find which roll a document is assigned to.
    
    Args:
        doc_name: Name of the document
        film_rolls: Dictionary containing film roll allocation
    
    Returns:
        Tuple of (film_type, roll_id) if found, (None, None) otherwise
    """
    # Check if the structure has '16mm' and '35mm' keys
    if '16mm' in film_rolls and 'rolls' in film_rolls['16mm']:
        for roll_id, roll_data in film_rolls['16mm']['rolls'].items():
            if "documents" in roll_data and doc_name in roll_data["documents"]:
                return ('16mm', roll_id)
    
    if '35mm' in film_rolls and 'rolls' in film_rolls['35mm']:
        for roll_id, roll_data in film_rolls['35mm']['rolls'].items():
            if "documents" in roll_data and doc_name in roll_data["documents"]:
                return ('35mm', roll_id)
    
    # Fallback to the original method for backward compatibility
    for roll_id, roll_data in film_rolls.items():
        if "documents" in roll_data and doc_name in roll_data["documents"]:
            return (None, roll_id)
    
    logger.debug(f"No roll found for document {doc_name}")
    return (None, None)

def get_film_number_for_roll(roll_id: str, film_rolls: Dict[str, Any]) -> Optional[str]:
    """
    Get the film number for a roll.
    
    Args:
        roll_id: ID of the roll
        film_rolls: Dictionary containing film roll allocation
    
    Returns:
        Film number if found, None otherwise
    """
    # Check if the structure has '16mm' and '35mm' keys
    if '16mm' in film_rolls and 'rolls' in film_rolls['16mm']:
        if roll_id in film_rolls['16mm']['rolls'] and "film_number" in film_rolls['16mm']['rolls'][roll_id]:
            return film_rolls['16mm']['rolls'][roll_id]["film_number"]
    
    if '35mm' in film_rolls and 'rolls' in film_rolls['35mm']:
        if roll_id in film_rolls['35mm']['rolls'] and "film_number" in film_rolls['35mm']['rolls'][roll_id]:
            return film_rolls['35mm']['rolls'][roll_id]["film_number"]
    
    # Fallback to the original method for backward compatibility
    if roll_id in film_rolls and "film_number" in film_rolls[roll_id]:
        return film_rolls[roll_id]["film_number"]
    
    logger.debug(f"Could not find film number for roll {roll_id}")
    return None





def process_no_oversize_documents(project_info: Dict[str, Any],
                                  document_pages: Dict[str, Any],
                                  film_rolls: Dict[str, Any]) -> None:
    """
    Processes documents for projects with NO oversized pages.
    Creates output directories based on film numbers and copies
    the corresponding documents into them.
    Does NOT handle document splitting yet.

    Args:
        project_info: Dictionary containing project metadata, including output_dir.
        document_pages: Dictionary mapping document names to their info (like source path).
        film_rolls: Dictionary containing the allocation of documents to rolls and film numbers.
    """
    logger.section("PROCESSING DOCUMENTS (NO OVERSIZES)")

    # --- Get Base Output Directory ---
    # Get the parent folder name from project_info
    parent_folder_name = next(iter(project_info.keys()))
    input_path = Path(project_info[parent_folder_name]["path"])
    output_dir = input_path.parent / ".output"
    project_info[parent_folder_name]["output_dir"] = str(output_dir)
    
    logger.info(f"Using output directory: {output_dir}")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Determine Roll Structure ---
    # Handle different possible structures of film_rolls
    roll_sections = {}
    film_type = None
    
    # Check for nested structure with film type keys
    if '16mm' in film_rolls and 'rolls' in film_rolls['16mm']:
        logger.info("Found 16mm rolls structure")
        roll_sections.update(film_rolls['16mm']['rolls'])
        film_type = '16mm'
    elif '35mm' in film_rolls and 'rolls' in film_rolls['35mm']:
        logger.info("Found 35mm rolls structure")
        roll_sections.update(film_rolls['35mm']['rolls'])
        film_type = '35mm'
    # Check for standard rolls structure
    elif 'rolls' in film_rolls:
        logger.info("Found standard rolls structure")
        roll_sections = film_rolls['rolls']
    # Fallback for flat structure
    else:
        logger.info("Using fallback for flat film_rolls structure")
        # Filter out non-roll entries
        roll_sections = {k: v for k, v in film_rolls.items() 
                        if isinstance(v, dict) and 'documents' in v}

    if not roll_sections:
        logger.error("No valid roll data found in film_rolls structure")
        return

    # --- Process Each Roll ---
    processed_files_count = 0
    errors_count = 0
    total_rolls = len(roll_sections)
    
    logger.info(f"Found {total_rolls} rolls to process")

    for roll_id, roll_data in roll_sections.items():
        film_number = roll_data.get("film_number")
        if not film_number:
            logger.warning(f"Skipping Roll ID '{roll_id}': Missing film number")
            continue

        # --- Create Roll Directory ---
        roll_output_dir = output_dir / str(film_number)
        try:
            roll_output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Processing Roll {film_number} (ID: {roll_id})")
        except OSError as e:
            logger.error(f"Failed to create directory {roll_output_dir}: {e}")
            errors_count += 1
            continue

        # --- Process Documents on Roll ---
        documents_on_roll = roll_data.get("documents", {})
        if not documents_on_roll:
            logger.info(f"Roll {film_number} has no documents assigned")
            continue

        doc_count = len(documents_on_roll)
        logger.info(f"Found {doc_count} documents on roll {film_number}")

        # Sort documents by their document_index to ensure consistent ordering
        sorted_documents = sorted(
            documents_on_roll.items(),
            key=lambda x: x[1].get("document_index", 1)
        )

        for doc_name, doc_roll_info in sorted_documents:
            # --- Find Document Source Path ---
            doc_info = document_pages.get(doc_name)
            if not doc_info:
                logger.error(f"Document '{doc_name}' not found in document_pages")
                errors_count += 1
                continue

            # Try different possible path keys
            source_path = None
            for path_key in ['path', 'source_path', 'filepath']:
                if path_key in doc_info and doc_info[path_key]:
                    source_path = Path(doc_info[path_key])
                    if source_path.is_file():
                        break
                    source_path = None

            if not source_path:
                logger.error(f"Valid source path not found for document '{doc_name}'")
                errors_count += 1
                continue

            # --- Check for Document Splitting ---
            # For now, we assume no splitting is needed
            is_split = False
            page_range = doc_roll_info.get("pagerange")
            
            # If page range doesn't cover the whole document, it needs splitting
            if page_range and doc_info.get("pages"):
                total_pages = doc_info.get("pages")
                if page_range[0] > 1 or page_range[1] < total_pages:
                    is_split = True
                    logger.warning(f"Document '{doc_name}' needs splitting (pages {page_range[0]}-{page_range[1]} of {total_pages}) - NOT IMPLEMENTED YET")
                    # Skip for now until splitting is implemented
                    continue

            # --- Generate Blip Information ---
            # Retrieve document index and frame range
            doc_index = doc_roll_info.get("document_index", 1)  # Default to 1 if missing
            frame_start, frame_end = doc_roll_info.get("frameRange", [0, 0])
            
            # Generate blip string in the format: "film_number-{doc_index:04d}.{frame_start:05d}"
            blip_str = f"{film_number}-{doc_index:04d}.{frame_start:05d}"
            
            # Store blip in film_rolls structure
            if film_type == '16mm' and '16mm' in film_rolls:
                if roll_id in film_rolls['16mm']['rolls']:
                    if doc_name in film_rolls['16mm']['rolls'][roll_id]['documents']:
                        film_rolls['16mm']['rolls'][roll_id]['documents'][doc_name]['blip'] = blip_str
                        #logger.debug(f"Added blip {blip_str} to 16mm document {doc_name} in film_rolls")
            elif film_type == '35mm' and '35mm' in film_rolls:
                if roll_id in film_rolls['35mm']['rolls']:
                    if doc_name in film_rolls['35mm']['rolls'][roll_id]['documents']:
                        film_rolls['35mm']['rolls'][roll_id]['documents'][doc_name]['blip'] = blip_str
                        #logger.debug(f"Added blip {blip_str} to 35mm document {doc_name} in film_rolls")
            elif 'rolls' in film_rolls:
                if roll_id in film_rolls['rolls']:
                    if doc_name in film_rolls['rolls'][roll_id]['documents']:
                        film_rolls['rolls'][roll_id]['documents'][doc_name]['blip'] = blip_str
                        #logger.debug(f"Added blip {blip_str} to document {doc_name} in film_rolls")
            else:
                # Fallback for flat structure
                if roll_id in film_rolls and 'documents' in film_rolls[roll_id]:
                    if doc_name in film_rolls[roll_id]['documents']:
                        film_rolls[roll_id]['documents'][doc_name]['blip'] = blip_str
                        #logger.debug(f"Added blip {blip_str} to document {doc_name} in film_rolls (flat structure)")
            
            # Also store in document_pages for reference
            if doc_name in document_pages:
                document_pages[doc_name]['blip'] = blip_str
                #logger.debug(f"Added blip {blip_str} to document {doc_name} in document_pages")

            # --- Copy Document ---
            destination_path = roll_output_dir / source_path.name
            
            try:
                shutil.copy2(source_path, destination_path)
                processed_files_count += 1
                #logger.info(f"Copied '{source_path.name}' to roll {film_number} with blip {blip_str}")
            except Exception as e:
                logger.error(f"Failed to copy '{source_path.name}' to '{destination_path}': {e}")
                errors_count += 1

    # --- Log Summary ---
    logger.success(f"Document processing complete: {processed_files_count} files copied to {total_rolls} roll directories")
    if errors_count > 0:
        logger.warning(f"Encountered {errors_count} errors during processing")













# ================================  FUTURE STAGES PROCESSING ===================================
# --------------------------------  INITIAL INDEX VALIDATION  ----------------------
"""
After the filming is finished, we get a log file, which we compare to the initial index to validate correct filming.

"""



def export_results(project_info: Dict[str, Any], document_pages: Dict[str, Any], 
                film_allocation: Dict[str, Any], film_rolls: Dict[str, Any], index_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Export results to JSON files.
    
    Args:
        project_info: Dictionary containing project metadata
        document_pages: Dictionary containing document information
        film_allocation: Dictionary containing film allocation information
        film_rolls: Dictionary containing film roll allocation
        index_data: Optional dictionary containing index data
    """
    
    logger.section("EXPORTING RESULTS")
    
    try:
        # Get the parent folder path from project_info
        parent_folder_name = next(iter(project_info.keys()))
        parent_folder_path = project_info[parent_folder_name].get("parentFolderPath", "")
        
        if not parent_folder_path:
            # Fallback to the path of the first document if parent folder path is not available
            if document_pages:
                first_doc = next(iter(document_pages.values()))
                if "path" in first_doc:
                    parent_folder_path = os.path.dirname(first_doc["path"])
                else:
                    # If no path is available, use the current directory
                    parent_folder_path = os.getcwd()
            else:
                # If no documents, use the current directory
                parent_folder_path = os.getcwd()
        
        # Create a data directory in the parent folder
        data_dir = os.path.join(parent_folder_path, ".data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Get archive ID for file naming
        archive_id = project_info[parent_folder_name].get("archiveId", "Unknown")
        
        # Create full paths for JSON files
        project_info_path = os.path.join(data_dir, f"{archive_id}_projectInfo.json")
        document_pages_path = os.path.join(data_dir, f"{archive_id}_documentPages.json")
        film_allocation_path = os.path.join(data_dir, f"{archive_id}_filmAllocation.json")
        film_rolls_path = os.path.join(data_dir, f"{archive_id}_filmRolls.json")
        index_data_path = os.path.join(data_dir, f"{archive_id}_index.json")
        
        # Export each JSON file
        with open(project_info_path, "w", encoding="utf-8") as f:
            json.dump(project_info, f, indent=4)
            logger.info(f"Exported project info to {project_info_path}")
            
        with open(document_pages_path, "w", encoding="utf-8") as f:
            json.dump(document_pages, f, indent=4)
            logger.info(f"Exported document pages to {document_pages_path}")
            
        with open(film_allocation_path, "w", encoding="utf-8") as f:
            json.dump(film_allocation, f, indent=4)
            logger.info(f"Exported film allocation to {film_allocation_path}")
            
        with open(film_rolls_path, "w", encoding="utf-8") as f:
            json.dump(film_rolls, f, indent=4)
            logger.info(f"Exported film rolls to {film_rolls_path}")
            
        # Export index data if provided
        if index_data:
            with open(index_data_path, "w", encoding="utf-8") as f:
                json.dump(index_data, f, indent=4)
                logger.info(f"Exported index data to {index_data_path}")
        
        # Update project_info with the data directory path for database use
        project_info[parent_folder_name]["data_dir"] = data_dir
        project_info[parent_folder_name]["index_path"] = index_data_path if index_data else ""
            
        logger.success(f"Successfully exported all results to JSON files in {data_dir}")
        
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}")

def open_explorer(input_folder_path):
    subprocess.run(f"explorer /select, {input_folder_path}")

def generate_blip(film_number: str, doc_index: int, frame_start: int) -> str:
    """Generate a blip string in the format: film_number-doc_index.frame_start"""
    return f"{film_number}-{doc_index:04d}.{frame_start:05d}"

def main() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Main function to orchestrate the document processing workflow.
    
    Returns:
        tuple: (project_info, document_pages, film_allocation, film_rolls, index_data)
    """
    
    logger.section("DOCUMENT PROCESSING WORKFLOW")
    
    
    # Get input folder path from command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == 'G':
        input_folder_path = r".\.testing\RRD017-2024_OU_GROSS\PDFs zu RRD018-2025"
        comlist_path = r"F:\pagifyZ\.testing\RRD017-2024_OU_GROSS\comlist.xlsx"
    elif len(sys.argv) > 1 and sys.argv[1] == 'K':
        input_folder_path = r".\.testing\RRD017-2024_OU_KLEIN\PDFs zu RRD018-2025"
        comlist_path = r"F:\pagifyZ\.testing\RRD017-2024_OU_KLEIN\comlist.xlsx"
    elif len(sys.argv) > 1 and sys.argv[1] == '1':
        input_folder_path = r"X:\RRD090-2024_OU_Triebwerksmontagebauakten\RRD090-2024"
        comlist_path = r"X:\RRD090-2024_OU_Triebwerksmontagebauakten\RRD090-2024_ComListe.xlsx"
    elif len(sys.argv) > 1 and sys.argv[1] == '2':
        input_folder_path = r"X:\RRD017-2024_OU_FAIR\PDFs zu RRD017-2024"
        comlist_path = r"X:\RRD017-2024_OU_FAIR\RRD017-2024_Comlist - FAIR.xls"
    # Filepath as argument
    elif len(sys.argv) > 1 and sys.argv[1]:
        input_folder_path = sys.argv[1]
        comlist_path = None
    elif len(sys.argv) > 1 and sys.argv[1] == 'F':
        # Use PowerShell to show folder browser dialog
        command = '''
        Add-Type -AssemblyName System.Windows.Forms
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        $folderBrowser.Description = "Select Project Folder"
        $folderBrowser.RootFolder = [System.Environment+SpecialFolder]::MyComputer
        $folderBrowser.SelectedPath = "X:\\"
        if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            $folderBrowser.SelectedPath
        }
        '''
        
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        input_folder_path = result.stdout.strip()
        if not input_folder_path:
            logger.critical("No folder selected. Exiting program.")
            sys.exit(1)
        comlist_path = None  # Will be determined later based on the selected folder
    else:
        logger.critical("Invalid argument. Please provide '1' or '2' as the argument.")
        raise ValueError("Invalid argument. Please provide '1' or '2' as the argument.")
    
    with logger.timer("Total Processing Time"):
        
        # Initialize project
        project_info, folder_path, folder_name, parent_folder_name, comlist_path = initialize_project(input_folder_path, comlist_path)
        
        # Process documents and identify oversized pages in a single step
        document_pages, has_oversized, total_oversized, documents_with_oversized = identify_oversized_pages(folder_path, project_info, parent_folder_name)
        
        # Get total page count from the processed documents
        total_page_count = project_info[parent_folder_name]["totalPages"]
        
        # Initialize film allocation structure
        film_allocation: Dict[str, Any] = {
            parent_folder_name: {
                "documentInfo": {
                    "totalReferences": 0,
                    "totalPages16": 0,
                    "totalPages35": 0,
                },
                "filmAllocation": {
                    "allocation16": 0,
                    "rolls16": 0,
                    "allocation35": 0,
                    "rolls35": 0
                }
            }
        }
        
        # Calculate reference pages
        reference_sheet_count = calculate_references(document_pages)
        
        # Update project info with total pages including references
        project_info[parent_folder_name]["totalPagesWithRefs"] = total_page_count + reference_sheet_count
        
        # Calculate film allocation
        film_allocation = calculate_film_allocation(
            parent_folder_name, 
            film_allocation, 
            document_pages, 
            total_page_count, 
            reference_sheet_count
        )
        
        # Allocate documents to film rolls
        
        logger.section("ALLOCATING DOCUMENTS TO FILM ROLLS")
        
        if document_pages:
            # state before allocation
            logger.debug(f"Before allocation: {len(document_pages)} documents found")
            logger.debug(f"Before allocation: oversized flag in project_info is {project_info[parent_folder_name]['oversized']}")
            logger.debug(f"Before allocation: {documents_with_oversized} documents marked as oversized")
            logger.debug(f"Before allocation: {total_oversized} total oversized pages")
            
            if not project_info[parent_folder_name]["oversized"]:
                logger.info("No oversized pages found, using standard allocation")
                film_rolls = no_oversizes(document_pages, parent_folder_name, folder_name, project_info)
            else:
                logger.info("Oversized pages found, using special allocation")
                film_rolls = has_oversizes(document_pages, parent_folder_name, folder_name, project_info)
                
            logger.success("Document allocation completed successfully")
        else:
            logger.warning("No documents to allocate")
            film_rolls = {}
        
        # Initialize index for tracking document locations on film rolls
        index_data = initialize_index(document_pages, comlist_path, film_rolls)
        
        # Assign film numbers to rolls
        try:
            
            logger.section("ASSIGNING FILM NUMBERS")
            
            logger.info("Assigning film numbers to rolls")

            # Get the parent folder path from project_info
            parent_folder_path = project_info[parent_folder_name].get("parentFolderPath", "")
            
            # Create a data directory in the parent folder
            data_dir = os.path.join(parent_folder_path, ".data")
            os.makedirs(data_dir, exist_ok=True)

            # Create full paths for index JSON files
            index_data_path = os.path.join(data_dir, f"{project_info[parent_folder_name]['archiveId']}_index.json")

            # Pass the project_info to properly populate the Projects table
            project_data = {
                "archive_id": project_info[parent_folder_name].get("archiveId", "Unknown"),
                "location": project_info[parent_folder_name].get("location", "Unknown"),
                "doc_type": project_info[parent_folder_name].get("doc_type", "Unknown"),
                "path": str(folder_path),
                "folderName": folder_name,
                "oversized": project_info[parent_folder_name].get("oversized", False),
                "total_pages": total_page_count,
                "data_dir": data_dir,
                "index_path": index_data_path
            }

            film_rolls, index_data = propagate_com_ids_and_assign_film_numbers(
                document_pages,
                film_rolls, 
                index_data,
                project_data
            )
            
            logger.success("Film numbers assigned successfully")
        except ImportError:
            logger.warning("Film number allocation module not found. Skipping film number assignment.")
        except Exception as e:
            logger.error(f"Error assigning film numbers: {str(e)}")


        try:
            if not project_info[parent_folder_name]["oversized"]:
                logger.info("Project has no oversized documents. Running simplified processing.")
                process_no_oversize_documents(project_info, document_pages, film_rolls)
            else:
                logger.info("Project has oversized documents. Running standard processing.")
                process_documents(project_info, document_pages, film_rolls, index_data) # Your original function
                logger.success("Document processing completed successfully")
        except Exception as e:
            logger.error(f"Error during document processing: {str(e)}")
            raise  # Re-raise to be caught by main error handler
        
        # Export results
        export_results(project_info, document_pages, film_allocation, film_rolls, index_data)

        # Open folder in explorer
        open_explorer(input_folder_path)
    
    logger.success("Document processing workflow completed successfully")
    return project_info, document_pages, film_allocation, film_rolls, index_data



# Execute the main function if this script is run directly
if __name__ == "__main__":
    try:
        project_info, document_pages, film_allocation, film_rolls, index_data = main()
        logger.info("Script completed successfully")
    except Exception as e:
        logger.critical(f"Script execution failed: {str(e)}")
        raise