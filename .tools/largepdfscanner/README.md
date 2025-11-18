# Large PDF Scanner

Scans a drive (e.g., `X:\`) where first-level folders are PROJECTS, finds `PDF` folders within them, checks PDFs for page counts exceeding a threshold (default: 2900 pages), and exports results to JSON.

## Features

- Scans from a root directory (e.g., `X:\`)
- First-level folders in the root are treated as PROJECT folders
- Within each PROJECT folder, finds folders named `PDF` (case-insensitive)
- Scans all PDF files in those `PDF` folders
- Ignores folders starting with "." (like `.output`)
- Ignores `sysvolinf` folders (case-insensitive)
- Ignores `RECYCLE.BIN` and `$RECYCLE.BIN` folders (case-insensitive)
- Checks page count using PyMuPDF
- Exports PDFs exceeding the threshold to JSON

## Requirements

- Python 3.x
- PyMuPDF (`pip install PyMuPDF`)
- tqdm (`pip install tqdm`)
- colorama (`pip install colorama`)

## Usage

### Basic Usage

```bash
python large_pdf_scanner.py X:\
```

This will:
- Scan `X:\` for first-level folders (these are the PROJECTS)
- Find `PDF` folders within each PROJECT
- Check all PDFs for page count > 2900
- Export results to `large_pdfs.json`

### Custom Threshold

```bash
python large_pdf_scanner.py X:\ --threshold 5000
```

### Custom Output File

```bash
python large_pdf_scanner.py X:\ --output my_results.json
```

### Combined Options

```bash
python large_pdf_scanner.py X:\ --threshold 5000 --output results.json
```

## Output Format

The JSON output contains:

```json
{
  "scan_date": "2025-01-20T10:30:00",
  "root_path": "X:\\",
  "page_threshold": 2900,
  "total_pdfs_scanned": 150,
  "large_pdfs_count": 5,
  "errors_count": 0,
  "large_pdfs": [
    {
      "path": "X:\\PROJECT1\\PDF\\document.pdf",
      "filename": "document.pdf",
      "page_count": 3500,
      "file_size_bytes": 104857600,
      "file_size_mb": 100.0,
      "project_folder": "X:\\PROJECT1",
      "pdf_folder": "X:\\PROJECT1\\PDF"
    }
  ],
  "errors": []
}
```

## Folder Structure

The tool expects this structure:

```
X:\
  PROJECT1\          (first-level folder = PROJECT)
    PDF\              (second-level folder)
      *.pdf
    .output\          (ignored - starts with ".")
    other folders...
  PROJECT2\           (first-level folder = PROJECT)
    PDF\              (second-level folder)
      *.pdf
  ...
```

## Notes

- Folders starting with "." are automatically ignored
- Only PDFs directly in `PDF` folders are scanned (not recursive within PDF folders)
- The tool uses PyMuPDF for fast page counting
- Progress is shown with a progress bar
- Errors reading PDFs are logged in the output JSON

