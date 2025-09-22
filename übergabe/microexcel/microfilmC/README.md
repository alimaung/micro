# Microfilm Processing System (C Implementation)

A C implementation of the microfilm processing system for managing document digitization, film allocation, and archival operations.

## Overview

This system processes PDF documents to:
- Detect oversized pages requiring special handling
- Allocate documents to 16mm and 35mm film rolls
- Generate film numbers and track document positions
- Export processing results and metadata
- Manage project data in SQLite database

## Features

- **Document Processing**: Automatic detection of oversized pages
- **Film Allocation**: Intelligent allocation to 16mm and 35mm film rolls
- **Database Integration**: SQLite database for tracking projects and film numbers
- **Export System**: JSON export of project data and film allocations
- **Logging**: Comprehensive logging with multiple levels
- **Command Line Interface**: Easy-to-use CLI with options

## Prerequisites

- GCC compiler with C99 support
- SQLite3 development libraries
- Make utility

### Installing Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install gcc make libsqlite3-dev
```

#### CentOS/RHEL/Fedora:
```bash
# CentOS/RHEL
sudo yum install gcc make sqlite-devel

# Fedora
sudo dnf install gcc make sqlite-devel
```

#### macOS:
```bash
# Using Homebrew
brew install gcc make sqlite3

# Using MacPorts
sudo port install gcc12 sqlite3
```

## Building

### Quick Build
```bash
make
```

### Build Options
```bash
# Debug build with symbols
make debug

# Optimized release build
make release

# Clean and rebuild
make rebuild

# Show all available targets
make help
```

## Installation

```bash
# Install to /usr/local/bin
make install

# Uninstall
make uninstall
```

## Usage

### Basic Usage
```bash
# Interactive mode (prompts for path)
./bin/microfilm

# Specify path directly
./bin/microfilm /path/to/project

# With debug output
./bin/microfilm --debug /path/to/project
```

### Command Line Options
- `-d, --debug`: Enable debug output
- `-h, --help`: Show help message

### Expected Project Structure

The system expects projects to follow this naming convention:
```
RRDxxx-xxxx_Location_DocType/
├── PDF/ (or similar document folder)
│   ├── 001.pdf
│   ├── 002.pdf
│   └── ...
└── RRDxxx-xxxx_Com.Liste.xls (optional COM list)
```

Examples:
- `RRD002-2025_OU_ZERTIFIKATE/`
- `RRD018-2024_DW_FAIR/`

### Output

The system creates several output directories and files:

```
project/
├── .data/           # JSON exports
│   ├── project_info.json
│   ├── documents.json
│   └── film_allocation.json
├── .logs/           # Log files
│   └── RRDxxx-xxxx.log
└── film_allocation.sqlite3  # Database
```

## Architecture

### Core Components

1. **Models** (`models.c`): Data structures and utility functions
2. **Project Service** (`project_service.c`): Project initialization and management
3. **Document Service** (`document_service.c`): PDF processing and oversized detection
4. **Film Service** (`film_service.c`): Film allocation algorithms
5. **Database** (`database.c`): SQLite operations and film number management
6. **Export Service** (`export_service.c`): JSON export functionality

### Data Flow

1. **Project Initialization**: Parse folder structure and extract metadata
2. **Document Processing**: Scan PDFs and detect oversized pages
3. **Reference Calculation**: Calculate reference sheet positions
4. **Film Allocation**: Allocate documents to film rolls
5. **Number Assignment**: Assign film numbers from database
6. **Export**: Generate JSON files and save to database

### Film Allocation Logic

#### Standard Projects (No Oversized Pages)
- Allocate all documents to 16mm film rolls
- Roll capacity: 2,900 pages
- Documents allocated in alphabetical order
- Split large documents across multiple rolls

#### Oversized Projects
- All documents → 16mm film (standard pages + references)
- Oversized pages only → 35mm film
- 16mm capacity: 2,900 pages
- 35mm capacity: 690 pages

## Configuration

### Film Capacities
- 16mm rolls: 2,900 pages
- 35mm rolls: 690 pages
- Padding for partial rolls: 150 pages

### Oversized Detection
- Width threshold: 842 points (A3 width)
- Height threshold: 1,191 points (A3 height)

## Development

### Code Style
```bash
# Format code
make format

# Static analysis
make check
```

### Building for Development
```bash
# Debug build with all symbols
make debug

# Run with debug output
./bin/microfilm --debug /path/to/test/project
```

### Testing
```bash
# Basic test
make test
```

## Error Handling

The system uses structured error handling with `MicrofilmError` structures:
- All functions return error status
- Detailed error messages provided
- Graceful cleanup on errors
- Comprehensive logging

## Logging

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General information
- `SUCCESS`: Successful operations
- `WARNING`: Warnings
- `ERROR`: Errors
- `CRITICAL`: Critical failures

### Log Output
- Console output with colors
- File logging in project directory
- Structured format with timestamps

## Database Schema

### Tables
- **Projects**: Project metadata and statistics
- **Rolls**: Film roll information and film numbers
- **Documents**: Document allocation and blip information
- **TempRolls**: Temporary roll tracking for partial rolls

### Film Number Format
- OU location: 1xxxxxxx (starts with 1)
- DW location: 2xxxxxxx (starts with 2)
- Other locations: 3xxxxxxx (starts with 3)

## Troubleshooting

### Common Issues

#### Build Errors
```bash
# Missing SQLite development headers
sudo apt install libsqlite3-dev

# GCC not found
sudo apt install gcc
```

#### Runtime Errors
- **"Cannot open database"**: Check SQLite installation and permissions
- **"Path does not exist"**: Verify project path is correct
- **"Invalid folder name format"**: Ensure folder follows RRDxxx-xxxx_Location_DocType pattern

### Debug Mode
```bash
# Enable debug logging
./bin/microfilm --debug /path/to/project
```

## Comparison with Python Version

### Advantages of C Implementation
- **Performance**: Significantly faster execution
- **Memory Usage**: Lower memory footprint
- **Dependencies**: Minimal runtime dependencies
- **Deployment**: Single executable file

### Trade-offs
- **PDF Processing**: Simplified (no actual PDF parsing in this demo)
- **Excel Reading**: Not implemented (would require additional libraries)
- **Development Time**: More complex than Python version

## License

This implementation follows the same licensing as the original Python version.

## Contributing

1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation
4. Use `make format` before committing

## Future Enhancements

- **PDF Library Integration**: Add mupdf or poppler for actual PDF processing
- **Excel Support**: Integrate libxlsxio for COM list reading
- **GUI Interface**: Optional GTK or Qt interface
- **Cross-platform**: Enhanced Windows support
- **Performance**: Multi-threading for large projects

