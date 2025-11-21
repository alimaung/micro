# Page Dimension Scanner

Comprehensive scanner to analyze page dimensions across PDF documents and compare different oversized page detection algorithms.

## Purpose

This scanner collects detailed dimension data from all pages in PDF documents to help answer critical questions about oversized page detection:

1. **What page sizes exist in our documents?** (A3, A4, Letter, custom, etc.)
2. **How do different detection algorithms perform?** (Compare all 4 methods side-by-side)
3. **What are the edge cases?** (Banners, scrolls, unusual dimensions)
4. **What's the real-world impact?** (How many more/fewer pages each method flags)

## Data Collected

### Per-Page Data
For each page in every PDF:
- Dimensions in points and inches
- Area in square inches
- Closest matching standard paper size
- Classification by all 4 detection methods:
  - **Edge-Based (AND logic)** - Current implementation
  - **Area-Based** - Surface area comparison
  - **Max-Dimension** - Maximum dimension check
  - **Smart-Fit** - Optimal rotation check

### Aggregate Statistics
- Total oversized pages per detection method
- Dimension histogram (grouped by size)
- Paper size distribution
- Detection method comparison (percentages)

### Output Analysis
The scanner produces data needed for:
- **Quantitative comparison** - Exact counts of oversized pages per method
- **Distribution analysis** - What page sizes are most common
- **Edge case identification** - Unusual dimensions that need special handling
- **Business decision support** - Data-driven choice of detection algorithm

## Installation

Requires Python 3.7+ and PyMuPDF:

```bash
pip install PyMuPDF tqdm colorama
```

## Usage

### Full Scan

```bash
python page_dimension_scanner.py X:\
```

### Quick Test (Sample Mode)

```bash
# Scan first 100 PDFs, analyze first 50 pages per PDF
python page_dimension_scanner.py X:\ --sample-pdfs 100 --sample-pages 50
```

### Custom Output File

```bash
python page_dimension_scanner.py X:\ --output my_analysis.json
```

## Output Format

### Console Output

```
📂 Starting dimension scan from: X:\
📐 A3 threshold: 11.7" × 16.5"

✅ Found 150 PROJECT folder(s)
✅ Found 1200 PDF file(s) to analyze

📊 Analyzing page dimensions...
[████████████████████] 1200/1200 PDFs

======================================================================
✅ Scan Complete!
======================================================================
📊 Total PDFs scanned: 1200
📄 Total pages analyzed: 125,000
❌ Errors: 5
💾 Results saved to: page_dimensions.json

Detection Method Comparison:
Method               Oversized Pages      Percentage     
-------------------------------------------------------
Edge-Based (AND)     1,234                0.99%
Area-Based           2,567                2.05%
Max-Dimension        3,456                2.76%
Smart-Fit            2,890                2.31%

Top 10 Paper Sizes Found:
  A4          :  98,450 pages (78.76%)
  A3          :  15,234 pages (12.19%)
  Letter      :   8,765 pages ( 7.01%)
  Custom      :   2,345 pages ( 1.88%)
  Tabloid     :     156 pages ( 0.12%)
  ...

Top 10 Page Dimensions (inches):
  8.3×11.7    :  98,450 pages (78.76%)
  11.7×16.5   :  15,234 pages (12.19%)
  8.5×11.0    :   8,765 pages ( 7.01%)
  11.0×17.0   :     156 pages ( 0.12%)
  ...
```

### JSON Output

```json
{
  "scan_date": "2024-01-15T10:30:00",
  "root_path": "X:\\",
  "a3_threshold": {
    "width_inches": 11.7,
    "height_inches": 16.5,
    "width_points": 842,
    "height_points": 1191
  },
  "statistics": {
    "total_pdfs_scanned": 1200,
    "total_pages_analyzed": 125000,
    "total_errors": 5,
    "detection_method_comparison": {
      "edge_based": {
        "total_oversized_pages": 1234,
        "percentage": 0.99
      },
      "area_based": {
        "total_oversized_pages": 2567,
        "percentage": 2.05
      },
      "max_dimension": {
        "total_oversized_pages": 3456,
        "percentage": 2.76
      },
      "smart_fit": {
        "total_oversized_pages": 2890,
        "percentage": 2.31
      }
    }
  },
  "dimension_histogram": {
    "8.3×11.7": 98450,
    "11.7×16.5": 15234,
    "8.5×11.0": 8765
  },
  "paper_size_histogram": {
    "A4": 98450,
    "A3": 15234,
    "Letter": 8765,
    "Custom": 2345
  },
  "pdf_analyses": [
    {
      "path": "X:\\PROJECT-001\\PDF\\doc1.pdf",
      "filename": "doc1.pdf",
      "project": "PROJECT-001",
      "total_pages": 100,
      "analyzed_pages": 100,
      "oversized_counts": {
        "edge_based": 5,
        "area_based": 8,
        "max_dimension": 10,
        "smart_fit": 9
      },
      "dimension_histogram": {...},
      "paper_size_histogram": {...}
    }
  ]
}
```

## Understanding the Results

### Detection Method Comparison

The key insight is the **difference** between methods:

```
Edge-Based (AND)     1,234 pages (0.99%)   ← Current (most conservative)
Area-Based           2,567 pages (2.05%)   ← +1,333 more pages
Max-Dimension        3,456 pages (2.76%)   ← +2,222 more pages (most aggressive)
Smart-Fit            2,890 pages (2.31%)   ← +1,656 more pages (recommended)
```

**Interpretation:**
- **Edge-Based** flags the fewest pages (current system)
- **Smart-Fit** flags ~2.3× more pages than current
- **Max-Dimension** is most aggressive (~2.8× more than current)

### Example Analysis

**Scenario 1: Close Results**
```
Edge-Based:     1,200 pages (1.0%)
Smart-Fit:      1,250 pages (1.04%)
Difference:     50 pages (0.04%)
```
→ **Conclusion:** Minimal difference, current logic is fine

**Scenario 2: Significant Difference**
```
Edge-Based:     1,200 pages (1.0%)
Smart-Fit:      3,600 pages (3.0%)
Difference:     2,400 pages (2.0%)
```
→ **Conclusion:** Current logic missing significant edge cases, consider updating

### Paper Size Distribution

Understanding what paper sizes exist helps validate detection logic:

```
A4:     78% ← Standard, should NOT be oversized
A3:     12% ← Threshold, should NOT be oversized
Custom:  8% ← Need to investigate
Tabloid: 2% ← 11"×17", slightly bigger than A3, SHOULD be oversized
```

### Dimension Histogram

Reveals actual page sizes in your data:

```
8.3×11.7   (A4):      78,000 pages
11.7×16.5  (A3):      15,000 pages
20.0×10.0  (Banner):     250 pages  ← Edge case!
8.5×11.0   (Letter):   8,000 pages
12.0×17.0  (Tabloid+): 1,200 pages  ← Should be oversized
```

## Analysis Workflow

### Step 1: Run Full Scan

```bash
python page_dimension_scanner.py X:\ --output production_dimensions.json
```

### Step 2: Review Detection Comparison

Check the **detection_method_comparison** in the JSON output:

```json
{
  "edge_based": {"total_oversized_pages": 1234, "percentage": 0.99},
  "smart_fit": {"total_oversized_pages": 2890, "percentage": 2.31}
}
```

**Calculate difference:**
- Smart-Fit flags 2890 - 1234 = **1,656 MORE pages** than current
- That's 1,656 pages currently going to 16mm that probably should go to 35mm

### Step 3: Investigate Edge Cases

Look at **dimension_histogram** for unusual sizes:

```json
{
  "20.0×10.0": 250,    // Wide banners
  "8.0×24.0": 100,     // Tall scrolls
  "12.5×12.5": 50      // Large squares
}
```

### Step 4: Make Decision

Based on:
1. **Difference magnitude** - How many more pages are flagged?
2. **Edge case types** - What unusual dimensions exist?
3. **Business impact** - Is missing these pages a problem?
4. **35mm film cost** - Is flagging more pages acceptable?

### Step 5: Implement and Validate

If changing detection logic:
1. Update code to use chosen method
2. Run scanner again with new logic
3. Compare before/after results
4. Spot-check sample PDFs manually

## Command-Line Options

### Full Scan (Production)
```bash
python page_dimension_scanner.py X:\
```
- Scans all PDFs
- Analyzes all pages
- ~2-5 minutes per 100 PDFs

### Quick Test (Development)
```bash
python page_dimension_scanner.py X:\ --sample-pdfs 50 --sample-pages 10
```
- Scans first 50 PDFs
- Analyzes first 10 pages per PDF
- ~30 seconds

### Custom Output
```bash
python page_dimension_scanner.py X:\ --output analysis_2024.json
```
- Saves to custom filename
- Useful for versioning/comparison

## Integration with Other Tools

### Compare with Large Range Scanner

```bash
# Run dimension scanner
python page_dimension_scanner.py X:\ --output dimensions.json

# Run large range scanner
cd ../largerangescanner
python large_range_scanner.py X:\ --output ranges.json

# Cross-reference results
# - dimensions.json tells you what pages are oversized by each method
# - ranges.json tells you which ranges exceed 35mm capacity
```

### Use Results for Decision Making

```python
import json

# Load scan results
with open('page_dimensions.json') as f:
    data = json.load(f)

# Calculate impact of changing detection logic
current = data['statistics']['detection_method_comparison']['edge_based']
proposed = data['statistics']['detection_method_comparison']['smart_fit']

difference = proposed['total_oversized_pages'] - current['total_oversized_pages']
percentage_increase = (difference / current['total_oversized_pages']) * 100

print(f"Switching to Smart-Fit would flag {difference} more pages")
print(f"That's a {percentage_increase:.1f}% increase")

# Estimate 35mm film impact
pages_per_35mm_roll = 690
additional_rolls = difference / pages_per_35mm_roll
print(f"Estimated additional 35mm rolls needed: {additional_rolls:.0f}")
```

## Performance Notes

- **Speed:** ~0.5-2 seconds per PDF (depending on page count and size)
- **Memory:** Efficient streaming, minimal memory usage
- **Output Size:** ~1-5 MB JSON for 1000 PDFs (without per-page data)

### Optimization Tips

**For large datasets:**
```bash
# Sample first 100 largest PDFs
python page_dimension_scanner.py X:\ --sample-pdfs 100
```

**For quick validation:**
```bash
# Sample 50 PDFs, 20 pages each
python page_dimension_scanner.py X:\ --sample-pdfs 50 --sample-pages 20
```

## Troubleshooting

### Error: "Directory not found"
- Check path format: `X:\` (Windows) or `/mnt/x` (Linux)
- Ensure drive is mounted and accessible

### Error: "No PDF files found"
- Verify PROJECT/PDF folder structure
- Check for hidden/system folders being skipped

### Output file is huge
- Use `--sample-pages` to limit per-PDF analysis
- The tool automatically excludes per-page data to keep files reasonable

## Author

Created for the microfilm allocation system to support data-driven decisions about oversized page detection logic.



