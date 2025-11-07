# Reanalyze Folders Management Command

## Overview
The `reanalyze_folders` command reprocesses existing analyzed folders with the corrected analysis logic that perfectly aligns with the register phase methodology.

## Why This Command Is Needed
Previously, there were inconsistencies between the analyze phase and register phase:

1. **Different oversized counting**: Analyze counted documents vs. register counted pages
2. **Inconsistent roll capacities**: Different values across phases  
3. **Incorrect 35mm logic**: 35mm rolls shown even without oversized pages
4. **Wrong utilization calculations**: Not matching actual allocation logic

This command fixes all analyzed folders to use the **exact same logic as the register phase**.

## Usage

### Basic Usage
```bash
# Reanalyze all folders
python manage.py reanalyze_folders

# Dry run to see what would change
python manage.py reanalyze_folders --dry-run

# Process in smaller batches
python manage.py reanalyze_folders --batch-size 5
```

### Advanced Usage
```bash
# Reanalyze specific folder
python manage.py reanalyze_folders --folder-path "X:\RRD011-2024_DW_R&O Zertifikate"

# Force reanalysis (ignores recent analysis timestamps)
python manage.py reanalyze_folders --force

# Combine options
python manage.py reanalyze_folders --dry-run --batch-size 3
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run` | Show what would be changed without actually doing it | False |
| `--force` | Force reanalysis even if recently analyzed | False |
| `--folder-path` | Reanalyze only a specific folder path | All folders |
| `--batch-size` | Number of folders to process per batch | 10 |

## What Gets Fixed

### 1. Oversized Counting
- **Before**: Counted documents with oversized pages
- **After**: Counts individual oversized pages (register-aligned)

### 2. Roll Capacities  
- **Before**: Mixed values (1500, 800, 2000, 3000)
- **After**: Consistent values (2940 for 16mm, 690 for 35mm)

### 3. 35mm Roll Logic
- **Before**: Always calculated 35mm rolls
- **After**: Only calculates 35mm when `has_oversized = True`

### 4. Reference Page Logic
- **Before**: Rough estimation (oversized × 2)
- **After**: Exact 1:1 ratio (1 reference per oversized page)

### 5. Utilization Calculation
- **Before**: Based on total pages for both film types
- **After**: 16mm uses total pages, 35mm uses oversized×2

## Expected Changes

For projects **without oversized pages**:
```
35mm rolls: 11 → 0
workflow: mixed_format → standard_16mm
```

For projects **with oversized pages**:
```
oversized: 5 docs → 23 pages
35mm rolls: 3 → 2 (more accurate)
utilization: 45% → 67% (corrected)
```

## Output Example

```
Starting reanalysis of existing analyzed folders...
Found 15 analyzed folders to process

Processing batch 1/2

Reanalyzing: X:\RRD011-2024_DW_R&O Zertifikate
  Original: 56 docs, 9408 pages, 0 oversized
  Original rolls: 6 x 16mm, 11 x 35mm
  ✓ Updated (2.34s): oversized: 0 → 0, 35mm rolls: 11 → 0, workflow: mixed_format → standard_16mm

Reanalyzing: X:\RRD099-2022_DW_SOADD
  Original: 23 docs, 456 pages, 3 oversized  
  Original rolls: 1 x 16mm, 1 x 35mm
  ✓ Updated (1.12s): oversized: 3 → 15, 35mm rolls: 1 → 2

============================================================
REANALYSIS COMPLETE
Total processed: 15
Updated: 12
No changes: 2
Errors: 1

12 folders were updated with corrected analysis logic!
```

## Safety Features

1. **Batch Processing**: Prevents system overload
2. **Error Handling**: Continues if individual folders fail
3. **Dry Run Mode**: Test changes before applying
4. **Change Tracking**: Shows exactly what changed
5. **Path Validation**: Checks folder existence
6. **Progress Reporting**: Real-time status updates

## When to Run

- **After logic updates**: When analysis algorithms change
- **Data migration**: When moving to new analysis standards  
- **Quality assurance**: To ensure consistency across phases
- **Before important analysis**: To guarantee accuracy

## Notes

- Uses `force_reanalyze=True` to override existing analysis
- Requires admin/staff user in database
- Small delay (0.1s) between folders to prevent overload
- Preserves original folder paths and timestamps
- Updates all analysis fields with corrected values 