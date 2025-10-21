import pandas as pd
import os

def analyze_excel_file():
    """
    Read db.xlsx file and extract first two rows from microapp_ sheets:
    - microapp_project
    - microapp_roll  
    - microapp_document
    - microapp_blip
    
    Save each as CSV file.
    """
    # Path to the Excel file (one directory up from current script)
    excel_file = r'db1.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    # Target sheet names
    target_sheets = ['microapp_project', 'microapp_roll', 'microapp_document', 'microapp_blip']
    
    try:
        # Read the Excel file to get all sheet names
        excel_file_obj = pd.ExcelFile(excel_file)
        available_sheets = excel_file_obj.sheet_names
        
        print(f"Available sheets: {available_sheets}")
        
        # Filter for sheets that start with 'microapp_'
        microapp_sheets = [sheet for sheet in available_sheets if sheet.startswith('microapp_')]
        print(f"Microapp sheets found: {microapp_sheets}")
        
        # Process each target sheet
        for sheet_name in target_sheets:
            if sheet_name in microapp_sheets:
                print(f"\nProcessing sheet: {sheet_name}")
                
                # Read only the first 2 rows (header + row 2)
                df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=2)
                
                # Create CSV filename
                csv_filename = f"{sheet_name}_sample.csv"
                csv_path = os.path.join(os.path.dirname(__file__), csv_filename)
                
                # Save as CSV
                df.to_csv(csv_path, index=False)
                print(f"Saved {csv_filename} with {len(df)} rows and {len(df.columns)} columns")
                
                # Display preview
                print("Preview:")
                print(df.head())
                
            else:
                print(f"Warning: Sheet '{sheet_name}' not found in Excel file")
        
        print(f"\nProcessing complete. CSV files saved in: {os.path.dirname(__file__)}")
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")

if __name__ == "__main__":
    analyze_excel_file()
