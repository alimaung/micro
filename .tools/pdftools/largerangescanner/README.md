# Large Oversized Range Scanner

Scans project directories for PDFs with oversized pages, groups consecutive oversized pages into ranges, and identifies ranges that exceed 35mm film capacity (690 pages).

## Purpose

This scanner helps identify edge cases in the microfilm allocation system where a single oversized range would exceed the 35mm roll capacity. This is important for:

1. **Understanding real-world data** - How often do large ranges actually occur?
2. **Validating allocation logic** - Ensuring the system can handle edge cases
3. **Planning capacity** - Knowing if special handling is needed

## What it Scans

### Oversized Pages
Pages are considered oversized if their dimensions exceed:
- **Width:** 11.7 inches (841 points)
- **Height:** 16.5 inches (1188 points)

### Ranges
Consecutive oversized pages are grouped into ranges. For example:
- Document with oversized pages [5, 6, 7, 10, 15, 16] creates 3 ranges:
  - Range 1: pages 5-7 (3 pages)
  - Range 2: page 10 (1 page)
  - Range 3: pages 15-16 (2 pages)

### 35mm Capacity
Each range requires:
- The oversized pages themselves
- 1 reference sheet (placed before the oversized pages)

**Example:** Range with pages 5-7 = 3 oversized pages + 1 reference = **4 pages on 35mm**

**Capacity:** 35mm film holds **690 pages**

A range is considered "large" if: `oversized_pages + 1 > 690`

## Installation

Requires Python 3.7+ and PyMuPDF:

```bash
pip install PyMuPDF tqdm colorama
```

## Usage

### Basic Usage

```bash
python large_range_scanner.py X:\
```

### With Custom Threshold

```bash
python large_range_scanner.py X:\ --threshold 500
```

### With Custom Output File

```bash
python large_range_scanner.py X:\ --output my_results.json
```

## Output

### Console Output

The scanner displays:
1. Progress bar during scanning
2. Summary statistics:
   - Total PDFs scanned
   - PDFs with oversized pages
   - Total oversized pages found
   - Total ranges found
   - Large ranges exceeding capacity
3. Range size distribution
4. List of PDFs with large ranges (top 10)

### JSON Output

The output file contains:

```json
{
  "scan_date": "2024-01-15T10:30:00",
  "root_path": "X:\\",
  "threshold_35mm": 690,
  "oversize_threshold_inches": {
    "width": 11.7,
    "height": 16.5
  },
  "statistics": {
    "total_pdfs_scanned": 1500,
    "pdfs_with_oversized": 45,
    "pdfs_with_large_ranges": 2,
    "total_oversized_pages": 3200,
    "total_ranges": 156,
    "total_large_ranges": 3,
    "range_size_distribution": {
      "0-100": 120,
      "101-200": 25,
      "201-300": 8,
      "301-400": 2,
      "401-500": 0,
      "501-600": 1,
      "601-690": 0,
      "691+": 3
    },
    "errors_count": 5
  },
  "pdfs_with_large_ranges": [
    {
      "path": "X:\\PROJECT-001\\PDF\\large_doc.pdf",
      "filename": "large_doc.pdf",
      "project_name": "PROJECT-001",
      "total_pages": 5000,
      "total_oversized": 900,
      "total_ranges": 3,
      "large_ranges": [
        {
          "start": 100,
          "end": 950,
          "oversized_pages": 851,
          "total_pages_35mm": 852
        }
      ],
      "large_ranges_count": 1
    }
  ],
  "pdfs_with_oversized": [...],
  "warnings": [...],
  "errors": [...]
}
```

## Understanding the Results

### No Large Ranges
```
✅ No large ranges found! All ranges fit within 35mm capacity.
```
**Meaning:** Your allocation logic doesn't need special handling for oversized ranges. Standard document-centric allocation will work fine.

### Large Ranges Found
```
🚨 PDFs with large ranges: 3
⚠️  PDFs with Large Ranges (>690 pages):
  1. huge_document.pdf
     Project: PROJECT-ALPHA
     Large ranges: 1
       - Pages 50-950: 901 pages on 35mm
```
**Meaning:** These PDFs have ranges that exceed 35mm capacity and will need to be split across multiple rolls.

## Integration with Allocation System

The findings from this scanner inform the 35mm allocation logic:

1. **If no large ranges exist:**
   - Use simple document-centric allocation
   - Each document's ranges go on dedicated rolls
   - No splitting logic needed

2. **If large ranges exist:**
   - Implement range splitting logic
   - Split large ranges at 690-page boundaries
   - Place reference sheet at start of first segment
   - Document the split in metadata

## Example Workflow

```bash
# 1. Scan your production data
python large_range_scanner.py X:\ --output production_ranges.json

# 2. Review the JSON output
# Check "total_large_ranges" in statistics

# 3. If large ranges exist, review the specific PDFs
# Check "pdfs_with_large_ranges" array

# 4. Decide on allocation strategy based on findings
```

## Directory Structure Expected

```
X:\
├── PROJECT-001/              # First-level: PROJECT folders
│   ├── PDF/                  # Second-level: PDF folder
│   │   ├── doc1.pdf
│   │   ├── doc2.pdf
│   │   └── SUBFOLDER/        # Optional: one level deeper
│   │       └── doc3.pdf
│   └── other_files...
├── PROJECT-002/
│   └── PDF/
│       └── ...
└── ...
```

## Notes

- Skips folders starting with "." (like `.output`)
- Skips system folders (System Volume Information, RECYCLE.BIN)
- Handles PDFs both directly in PDF folder and one level deeper
- Provides warnings for ambiguous folder structures
- Logs errors for unreadable PDFs

## Author

Created for the microfilm allocation system to validate edge case handling.



