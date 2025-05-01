# Barcode File Manager

A visually stunning, modern, and Material Design-themed Flask web interface for renaming files with sequential barcodes.

## Features

- Modern Material Design UI with dark/light mode
- File filtering by PDF and DOCX extensions
- Automatic barcode assignment starting from a specified number
- Real-time updating of document-to-barcode mappings
- Progress tracking with visual indicators
- Responsive design

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Flask

### Installation

1. Clone this repository or download the files

2. Install the required packages:
   ```
   pip install flask
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## How to Use

1. **Select Source Folder**:
   - Click the "Browse" button to select a folder containing the files you want to rename
   - You can also manually enter the path in the text field
   - Optionally filter by PDF or DOCX files by checking the corresponding boxes

2. **Set First Barcode**:
   - Enter the starting barcode number in the "First Barcode" field (default is 1)
   - Each file will be assigned sequential barcodes starting from this number

3. **View File Mappings**:
   - After selecting a source folder, the interface will display all files and their mapped barcodes
   - Files are sorted alphabetically

4. **Select Target Folder**:
   - Click the "Browse" button to select a destination folder for the renamed files
   - You can also manually enter the path in the text field

5. **Export Files**:
   - Click the "Export Files" button to start the renaming and copying process
   - The progress section will update in real-time to show the current status

## Troubleshooting

- If you encounter permission errors, make sure you have write access to the target folder
- For large file operations, the process may take some time to complete

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Built with Flask and MaterializeCSS
- Uses modern web technologies for a responsive interface 