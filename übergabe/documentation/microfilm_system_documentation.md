# Microfilm Processing System - Technical Documentation

## Overview

The Microfilm Processing System is a sophisticated document management and film allocation system designed for archival microfilm production. It processes PDF documents, identifies oversized pages, allocates them to different film types (16mm and 35mm), manages film roll capacity, assigns unique film numbers, and generates reference sheets for oversized documents.

## System Architecture

### Core Components

1. **Project Initialization** - Extracts metadata from folder structures
2. **Document Processing** - Analyzes PDFs and identifies oversized pages
3. **Film Allocation** - Distributes documents across film rolls
4. **Film Number Management** - Assigns unique identifiers with location-based prefixes
5. **Database Management** - SQLite-based persistence for roll tracking
6. **Reference Sheet Generation** - Creates PDF reference sheets for oversized documents
7. **Document Manipulation** - Handles document splitting and copying

### Key Constants

```python
OVERSIZE_THRESHOLD_WIDTH = 842      # Points (A3 width)
OVERSIZE_THRESHOLD_HEIGHT = 1191    # Points (A3 height)
CAPACITY_16MM = 2900               # Pages per 16mm roll
CAPACITY_35MM = 690                # Pages per 35mm roll
TEMP_ROLL_PADDING_16MM = 150       # Padding for 16mm temp rolls
TEMP_ROLL_PADDING_35MM = 150       # Padding for 35mm temp rolls
TEMP_ROLL_MIN_USABLE_PAGES = 100   # Minimum usable pages for temp rolls
```

## Detailed Processing Steps

### 1. Project Initialization (`initialize_project`)

**Purpose**: Extract project metadata from folder paths and names.

**Input**: 
- `input_folder_path`: Path to folder containing PDF documents
- `comlist_path`: Optional path to Excel file with document mappings

**Process**:
1. Parse folder structure to extract:
   - Archive ID (format: RRDxxx-xxxx)
   - Location code (OU or DW)
   - Document type (from folder name suffix)
2. Locate Excel comlist file in parent directory
3. Initialize logging system with project-specific paths

**Output**: 
```python
project_info = {
    "parent_folder_name": {
        "path": str,                    # Full path to folder
        "folderName": str,              # Folder name
        "parentFolderName": str,        # Parent folder name
        "parentFolderPath": str,        # Parent folder path
        "archiveId": str,               # Archive ID (e.g., "RRD018-2024")
        "location": str,                # Location code (e.g., "DW" or "OU")
        "doc_type": str,                # Document type (e.g., "FAIR")
        "oversized": bool,              # Whether project contains oversized pages
        "totalPages": int,              # Total number of pages
        "comlist_path": str             # Path to Excel comlist file
    }
}
```

### 2. Document Processing and Oversized Page Detection (`identify_oversized_pages`)

**Purpose**: Process all PDF documents, extract page information, and identify oversized pages.

**Process**:
1. **PDF Analysis**: For each PDF document:
   - Extract total page count using PyPDF2
   - Analyze each page's dimensions from mediabox
   - Check if page exceeds A3 size threshold (842x1191 points)
   - Handle both portrait and landscape orientations

2. **Oversized Page Detection**:
   ```python
   is_oversized = ((width > OVERSIZE_THRESHOLD_WIDTH and height > OVERSIZE_THRESHOLD_HEIGHT) or
                   (width > OVERSIZE_THRESHOLD_HEIGHT and height > OVERSIZE_THRESHOLD_WIDTH))
   ```

3. **Range Calculation**: Group consecutive oversized pages into ranges for efficient processing

4. **Reference Page Planning**: Calculate where reference sheets need to be inserted

**Output**:
```python
document_pages = {
    "document_name": {
        "path": str,                           # Full path to PDF
        "pages": int,                          # Total pages
        "oversized": bool,                     # Has oversized pages
        "totalOversized": int,                 # Count of oversized pages
        "dimensions": List[Tuple],             # (width, height, page_index, percent_over)
        "ranges": List[Tuple[int, int]],       # Page ranges (start, end)
        "readable_pages": List[str],           # Human-readable ranges
        "adjusted_ranges": List[Tuple],        # Ranges adjusted for reference sheets
        "references": {
            "pages": List[int],                # Reference page positions
            "totalReferences": int             # Total reference sheets needed
        }
    }
}
```

### 3. Film Allocation Calculation (`calculate_film_allocation`)

**Purpose**: Determine how many film rolls are needed for the project.

**Process**:
1. **16mm Allocation**: All document pages + reference sheets
2. **35mm Allocation**: Only oversized pages + reference sheets
3. **Roll Calculation**: Divide total pages by film capacity (ceiling division)

**Output**:
```python
film_allocation = {
    "parent_folder_name": {
        "documentInfo": {
            "totalReferences": int,    # Total reference sheets
            "totalPages16": int,       # Pages for 16mm film
            "totalPages35": int,       # Pages for 35mm film
            "location": str            # Project location
        },
        "filmAllocation": {
            "allocation16": int,       # Pages allocated to 16mm
            "rolls16": int,           # Number of 16mm rolls needed
            "allocation35": int,       # Pages allocated to 35mm
            "rolls35": int            # Number of 35mm rolls needed
        }
    }
}
```

### 4. Document-to-Roll Allocation

#### 4.1 No Oversized Pages (`no_oversizes`)

**Purpose**: Allocate documents to 16mm film rolls when no oversized pages exist.

**Strategy**:
- Documents are NOT split across rolls unless they exceed roll capacity (2900 pages)
- Documents are processed in alphabetical order
- Each roll tracks document index for blip generation

**Process**:
1. Initialize first roll with full capacity
2. For each document:
   - Check if it fits in current roll
   - If not, create new roll
   - Calculate frame ranges and document indices
   - Generate blip strings for tracking

#### 4.2 With Oversized Pages (`has_oversizes`)

**Purpose**: Allocate documents using both 16mm and 35mm film types.

**Strategy**:
- 16mm: All pages (regular + oversized + reference sheets)
- 35mm: Only oversized pages + reference sheets
- Complex segment-based allocation for documents with oversized ranges

**Process**:
1. **16mm Allocation**:
   - Process documents in alphabetical order
   - Create segments for regular pages and atomic units (reference + oversized range)
   - Allocate segments to rolls maintaining atomic unit integrity

2. **35mm Allocation** (`allocate_35mm_strict`):
   - Process only documents with oversized pages
   - Allocate oversized pages + reference sheets
   - Handle document splitting across multiple 35mm rolls

### 5. Film Number Assignment System

#### 5.1 Database Schema

**Projects Table**:
```sql
CREATE TABLE Projects (
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
```

**Rolls Table**:
```sql
CREATE TABLE Rolls (
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
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
)
```

**TempRolls Table**:
```sql
CREATE TABLE TempRolls (
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
    chain_position INTEGER NULL
)
```

**Documents Table**:
```sql
CREATE TABLE Documents (
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
```

#### 5.2 Film Number Generation (`get_next_film_number`)

**Purpose**: Generate unique film numbers based on project location.

**Format**: 8-digit numbers with location-based prefixes
- OU location: 1xxxxxxx (e.g., 10000001)
- DW location: 2xxxxxxx (e.g., 20000001)
- Other locations: 3xxxxxxx (e.g., 30000001)

**Process**:
1. Query database for highest existing film number with same prefix and location
2. Increment by 1
3. Return formatted 8-digit string

#### 5.3 Roll Processing (`process_16mm_rolls`, `process_35mm_rolls`)

**Purpose**: Assign film numbers to rolls with database persistence.

**16mm Roll Processing**:
1. Check for existing temp rolls with sufficient capacity
2. If found, use temp roll and create new temp roll from remainder
3. If not found, assign new film number
4. Create temp roll from partial rolls with sufficient capacity

**35mm Roll Processing**:
1. Look for active 35mm rolls with remaining capacity (location-aware)
2. If found, reuse existing roll and update usage
3. If not found, assign new film number
4. Track roll relationships and usage patterns

### 6. Index Management (`initialize_index`, `update_index_data`)

**Purpose**: Create and maintain index for tracking document locations on film rolls.

**Process**:
1. **Initialize Index**:
   - Read Excel comlist file to map document names to COM IDs
   - Create index entries for each document with initial roll assignments
   - Only process 16mm rolls (35mm intentionally excluded)

2. **Update Index**:
   - Update index entries with assigned film numbers
   - Generate blip strings in format: `film_number-document_index.frame_start`
   - Track roll sources (temp roll, shared roll, or direct assignment)

**Index Entry Format**:
```python
index_entry = [
    document_name,      # Barcode/document name
    com_id,            # COM ID from Excel file
    initial_index,     # [roll_id, frame_start, frame_end]
    final_index,       # Blip string with film number
    document_index     # Position on roll
]
```

### 7. Reference Sheet Generation (`create_reference_sheet`)

**Purpose**: Generate PDF reference sheets for oversized documents.

**Process**:
1. Create PDF using ReportLab
2. Include metadata:
   - Film number
   - Archive ID
   - Blip (location on film)
   - Document type
   - Human-readable page ranges
   - Document barcode

**Reference Sheet Content**:
```
Filmnumber: 10000001
Archive ID: RRD018-2024
Blip: 10000001-0001.00001
Doc-Type: FAIR
Human ranges: 1 von 2
Barcode: 1427007501013191
```

### 8. Document Processing and Output Generation

#### 8.1 Projects with Oversized Pages (`process_documents`)

**Purpose**: Process documents requiring reference sheets and special handling.

**Process**:
1. Create temporary directory structure:
   - `references/` - Reference sheet PDFs
   - `oversizes/` - Extracted oversized pages
   - `referenced/` - Documents with reference sheets prepended

2. For each oversized document:
   - Generate reference sheets for each oversized range
   - Extract oversized pages to separate document
   - Prepend reference sheets to oversized document
   - Copy files to film number-based directories

#### 8.2 Projects without Oversized Pages (`process_no_oversize_documents`)

**Purpose**: Simple document copying for projects without oversized pages.

**Process**:
1. Create output directories based on film numbers
2. Copy documents to appropriate roll directories
3. Generate blip strings for tracking
4. Handle document splitting (when implemented)

### 9. Blip Generation (`generate_blip`)

**Purpose**: Create unique identifiers for document locations on film.

**Format**: `film_number-document_index.frame_start`
- `film_number`: 8-digit film number
- `document_index`: 4-digit document position on roll
- `frame_start`: 5-digit starting frame number

**Example**: `10000001-0001.00001`

### 10. Export and Results Management (`export_results`)

**Purpose**: Export all processing results to JSON files for persistence and analysis.

**Output Files**:
- `{archive_id}_projectInfo.json` - Project metadata
- `{archive_id}_documentPages.json` - Document information
- `{archive_id}_filmAllocation.json` - Film allocation calculations
- `{archive_id}_filmRolls.json` - Roll assignments and film numbers
- `{archive_id}_index.json` - Document index with blips

## Key Algorithms and Data Structures

### 1. Oversized Page Detection Algorithm

```python
def detect_oversized_page(width, height):
    """Detect if page exceeds A3 size threshold"""
    return ((width > OVERSIZE_THRESHOLD_WIDTH and height > OVERSIZE_THRESHOLD_HEIGHT) or
            (width > OVERSIZE_THRESHOLD_HEIGHT and height > OVERSIZE_THRESHOLD_WIDTH))
```

### 2. Range Grouping Algorithm

```python
def group_consecutive_pages(page_numbers):
    """Group consecutive page numbers into ranges"""
    ranges = []
    for _, g in groupby(enumerate(sorted(page_numbers)), lambda x: x[0] - x[1]):
        group = list(map(itemgetter(1), g))
        if len(group) > 1:
            ranges.append((group[0], group[-1]))
        else:
            ranges.append((group[0], group[0]))
    return ranges
```

### 3. Film Number Allocation Algorithm

```python
def allocate_film_numbers(film_rolls, project_data):
    """Assign film numbers with temp roll optimization"""
    for roll in film_rolls:
        if roll.is_partial():
            temp_roll = find_suitable_temp_roll(roll.pages_needed)
            if temp_roll:
                roll.film_number = get_next_film_number(location)
                create_temp_roll_from_remainder(temp_roll, roll)
            else:
                roll.film_number = get_next_film_number(location)
        else:
            roll.film_number = get_next_film_number(location)
```

### 4. Segment-Based Allocation Algorithm

```python
def allocate_document_segments(document, ranges):
    """Allocate document segments maintaining atomic unit integrity"""
    segments = []
    current_page = 1
    
    for range_start, range_end in ranges:
        # Regular pages before range
        if current_page < range_start:
            segments.append({
                "type": "regular",
                "start": current_page,
                "end": range_start - 1
            })
        
        # Atomic unit (reference + range)
        segments.append({
            "type": "atomic",
            "start": range_start,
            "end": range_end + 1  # +1 for reference sheet
        })
        
        current_page = range_end + 1
    
    return segments
```

## Error Handling and Validation

### 1. Input Validation
- Verify folder paths exist and contain PDF files
- Validate Excel comlist file format and content
- Check document page counts and dimensions

### 2. Database Transaction Safety
- Use database transactions for atomic operations
- Implement rollback on errors
- Validate foreign key relationships

### 3. File System Safety
- Create directories with proper permissions
- Handle file copy errors gracefully
- Validate file paths and existence

### 4. Memory Management
- Process large documents in chunks
- Use generators for large datasets
- Implement proper cleanup of temporary files

## Performance Considerations

### 1. Database Optimization
- Use prepared statements for repeated queries
- Implement proper indexing on frequently queried columns
- Batch database operations when possible

### 2. File Processing
- Process PDFs in parallel where possible
- Use memory-efficient PDF reading
- Implement progress tracking for large projects

### 3. Memory Usage
- Stream large files instead of loading entirely into memory
- Use generators for large document collections
- Implement proper cleanup of temporary objects

## Integration Points

### 1. External Dependencies
- **PyPDF2**: PDF document processing
- **xlwings**: Excel file reading
- **ReportLab**: PDF generation
- **SQLite3**: Database operations
- **tkinter**: File dialog (optional)

### 2. File System Integration
- Input: PDF documents in specified folder structure
- Output: Organized directories by film number
- Temporary: Reference sheets and processed documents

### 3. Database Integration
- Persistent storage of roll assignments
- Film number tracking across projects
- Document-to-roll mapping

## Configuration and Customization

### 1. Film Capacity Settings
```python
CAPACITY_16MM = 2900  # Adjustable based on film specifications
CAPACITY_35MM = 690   # Adjustable based on film specifications
```

### 2. Oversized Page Thresholds
```python
OVERSIZE_THRESHOLD_WIDTH = 842   # Points (A3 width)
OVERSIZE_THRESHOLD_HEIGHT = 1191 # Points (A3 height)
```

### 3. Location-Based Film Number Prefixes
```python
def get_film_prefix(location):
    return "1" if location == "OU" else "2" if location == "DW" else "3"
```

## Testing and Validation

### 1. Unit Testing Requirements
- Test oversized page detection with various page sizes
- Validate film number generation and uniqueness
- Test roll allocation algorithms with edge cases
- Verify database operations and transactions

### 2. Integration Testing
- Test complete workflow with sample projects
- Validate file system operations
- Test Excel file reading and COM ID mapping
- Verify reference sheet generation

### 3. Performance Testing
- Test with large document collections
- Validate memory usage with large PDFs
- Test database performance with many rolls
- Measure processing time for various project sizes

## Deployment Considerations

### 1. System Requirements
- Python 3.7+ with required packages
- SQLite3 database support
- File system write permissions
- Excel file access (xlwings)

### 2. Environment Setup
- Install required Python packages
- Configure database file location
- Set up logging directory structure
- Configure Excel application access

### 3. Monitoring and Logging
- Comprehensive logging throughout processing
- Progress tracking for long-running operations
- Error reporting and recovery
- Performance metrics collection

This documentation provides a complete technical specification for recreating the microfilm processing system. Each component is detailed with its purpose, inputs, outputs, and implementation considerations, enabling another developer to understand and implement the system from scratch.
