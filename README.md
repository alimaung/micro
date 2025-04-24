# Microfilm Processing System

A comprehensive Python-based system for archiving PDF documents to microfilm with specialized handling for standard and oversized documents.

## Overview

The Microfilm Processing System automates the preparation, allocation, and distribution of electronic documents (primarily PDFs) for microfilm archiving. It handles critical aspects such as document analysis, film allocation, and reference management to ensure efficient preservation of documents on both 16mm and 35mm microfilm formats.

## System Architecture

The system is divided into three main processing phases:

1. **Register** - Analyzes documents and prepares them for filming (implemented in this codebase)
2. **Film** - Processes the documents to physical film using SMA software
3. **Handoff** - Post-processes and reports results

## Register Process

The Register phase handles the initial preparation of documents and consists of the following steps:

### 1. Project Initialization
- Parses project folders and initializes basic project information
- Extracts archive IDs, location codes, and document types
- Sets up logging and project structure

### 2. Document Analysis
- Analyzes PDF documents for total page count
- Identifies oversized pages that require special handling
- Calculates document dimensions and determines appropriate film formats

### 3. Reference Sheet Calculation
- For projects with oversized pages, calculates where reference sheets need to be inserted
- Creates relationships between standard (16mm) and oversized (35mm) documents

### 4. Film Pre-Allocation
- Allocates documents to film rolls based on capacity constraints
- Handles both 16mm (standard) and 35mm (oversized) film formats
- Manages document splitting across multiple rolls when necessary
- Tracks roll utilization and optimizes document placement

### 5. Film Number Allocation
- Assigns permanent film numbers to rolls from the database
- Manages temporary roll creation and allocation
- Updates index data with film numbers and document locations

### 6. Document Distribution
- Distributes documents to roll directories based on allocation
- For oversized documents:
  - Creates reference sheets linking 16mm to 35mm film
  - Extracts oversized pages for 35mm filming
  - Modifies PDFs as needed
- Organizes files for the Film phase

## Film Types and Handling

The system supports two film types with different handling:

- **16mm Film**: Used for standard documents and non-oversized portions of documents
  - Capacity: ~2,900 pages per roll
  
- **35mm Film**: Used specifically for oversized pages
  - Capacity: ~110 pages per roll
  - Preserves readability of large format documents
  - Reference sheets on 16mm point to corresponding 35mm frames

## Outputs

The Register process produces:

- **Database Entries**: Records projects, rolls, documents, and film numbers
- **Roll Directories**: Organized document files ready for filming
- **Data Files**: JSON files with allocation and index information
- **Reference Sheets**: For documents with oversized pages
- **Modified PDFs**: Prepared for optimal filming

## Dependencies

- Python
- SMA software (for the Film phase)
- ESP (for document processing)

## Usage

```
python main.py [path] [--debug]
```

Where:
- `path`: Path to the project folder or document subfolder
- `--debug`: Optional flag to show detailed debug information

## Components and Services

The system is built with a modular architecture using the following key services:

- **ProjectService**: Manages project initialization and configuration
- **DocumentProcessingService**: Analyzes documents and calculates references
- **FilmService**: Allocates documents to film rolls
- **FilmNumberService**: Handles film number allocation and database operations
- **DocumentDistributionService**: Distributes documents to roll directories
- **ReferenceSheetService**: Creates reference sheets for oversized documents
- **IndexService**: Manages index data for document tracking
- **ExportService**: Exports project results and data

## Workflow Example

1. System initializes a project from a folder containing PDF documents
2. Documents are analyzed to determine page counts and identify oversized pages
3. If oversized pages are detected, reference sheets are calculated
4. Documents are allocated to film rolls (16mm and 35mm if needed)
5. Film numbers are assigned to rolls from the database
6. Documents are distributed to roll directories
7. The system produces output files and database entries
8. The Film phase can then process each roll directory separately

## Data Model

The system uses a comprehensive data model including:
- Project metadata and settings
- Document information and page characteristics
- Film roll allocation and utilization
- Reference relationships between documents
- Distribution results and statistics

## Future Development

This codebase implements the Register phase. The Film and Handoff phases are works in progress.

