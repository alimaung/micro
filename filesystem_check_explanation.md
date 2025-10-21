# Filesystem Integrity Check - Explanation

## What the script checks:

### 1. **Orphaned Roll Directories**
- **Location**: Inside project `.output` directories
- **Format**: 8-digit numbers starting with 1 or 2 (e.g., `10000001`, `20000001`)
- **Problem**: These directories exist on the filesystem but have no corresponding Roll record in the database
- **Cause**: Usually happens when:
  - Projects are deleted from database but files remain
  - Roll records are deleted but directories remain
  - Manual file operations outside the application

### 2. **Orphaned Directories** (top-level)
- **Location**: Root drives (X:\, Y:\, Z:\)
- **Format**: Project directory names (e.g., `RRD072-2023_OU_Triebwerksakten`)
- **Problem**: Entire project directories exist but have no Project record in database
- **Cause**: Projects deleted from database but directories not cleaned up

### 3. **Orphaned Document Files**
- **Location**: Inside roll directories (e.g., `X:\Project\.output\10000001\`)
- **Format**: PDF files (e.g., `1427004807000278.pdf`)
- **Problem**: PDF files exist but have no corresponding Document or ProcessedDocument record
- **Cause**: 
  - Document records deleted but files remain
  - Files copied manually
  - Processing errors

## Fixes Applied:

### 1. **Improved Roll Directory Detection**
```python
# OLD (too broad):
if dir_name.isdigit() and len(dir_name) >= 8:
    return True

# NEW (specific format):
if (dir_name.isdigit() and 
    len(dir_name) == 8 and 
    dir_name.startswith(('1', '2'))):
    return True
```

### 2. **Better Path Handling**
- Added Unicode path support for German characters (ä, ö, ü)
- Added proper error handling for permission issues
- Added case-insensitive file extension matching (.pdf, .PDF)

### 3. **Improved Document Matching**
- Handle double extensions (.pdf.pdf)
- Fuzzy matching for document IDs
- Better database query logic

### 4. **Enhanced Directory Structure Logic**
- Look for `.output` subdirectories first
- Fall back to main directory if no `.output` found
- Only check actual roll directories (8-digit format)

## Example Issues and Solutions:

### Issue 1: False "Missing Directory"
```
"Missing roll directory: X:\RRD203-2019_DW_PSTA_Nachlieferungen\.output\20000001"
```
**Cause**: Directory exists but script couldn't find it due to Unicode or case issues
**Fix**: Better path resolution and case-insensitive checking

### Issue 2: False "Orphaned Document"
```
"Orphaned document file: X:\RRD013-2022_OU_Arbeitspläne\.output\10000001\1427004807000278.pdf"
```
**Cause**: Document exists in database but matching logic was too strict
**Fix**: Improved fuzzy matching and better database queries

### Issue 3: Wrong "Orphaned Roll Directory"
```
"Orphaned roll directory: X:\RRD072-2023_OU_Triebwerksakten\PDFs zu RRD072-2023"
```
**Cause**: Script was checking non-roll directories as if they were roll directories
**Fix**: Strict 8-digit format checking for roll directories only

## Usage:

```bash
# Full check with export
python check_filesystem_integrity.py export results.json

# Debug mode (shows detailed matching info)
python check_filesystem_integrity.py debug

# Check specific project
python check_filesystem_integrity.py project 88

# Find only orphaned directories
python check_filesystem_integrity.py orphans
```
