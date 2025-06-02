import pandas as pd
import re
import csv
from pathlib import Path

def extract_archive_id(directory_name):
    """Extract archive ID from directory name using regex (e.g., RRD262-2018)"""
    match = re.match(r'(RRD\d+-\d+)', directory_name)
    return match.group(1) if match else None

def read_excel_data(excel_path):
    """Read Excel file and create dictionary mapping archive IDs to cost dept and customer"""
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        # Create dictionary to store mappings
        archive_mapping = {}
        
        # Iterate through rows to find archive ID mappings
        for index, row in df.iterrows():
            # Look for archive ID pattern in columns B, D, E (assuming 0-indexed: 1, 3, 4)
            if len(row) > 4:  # Ensure we have enough columns
                archive_id = None
                cost_dept = None
                customer = None
                
                # Check each cell in the row for archive ID pattern
                for col_idx, cell_value in enumerate(row):
                    if pd.notna(cell_value) and isinstance(cell_value, str):
                        # Check if this cell contains an archive ID
                        archive_match = re.search(r'RRD\d+-\d+', str(cell_value))
                        if archive_match:
                            archive_id = archive_match.group(0)
                            
                            # Try to get cost dept and customer from adjacent columns
                            # Assuming structure: Archive ID, Cost Dept, Customer
                            try:
                                if col_idx + 3 < len(row) and pd.notna(row.iloc[col_idx + 2]):
                                    cost_dept = str(row.iloc[col_idx + 2]).strip()
                                if col_idx + 4 < len(row) and pd.notna(row.iloc[col_idx + 3]):
                                    customer = str(row.iloc[col_idx + 3]).strip()
                            except:
                                pass
                            
                            if archive_id and (cost_dept or customer):
                                archive_mapping[archive_id] = {
                                    'cost_dept': cost_dept or '',
                                    'customer': customer or ''
                                }
                            break
        
        return archive_mapping
    
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {}

def process_results_csv(results_csv_path, excel_path, output_csv_path):
    """Process results.csv and create new CSV with archive ID, cost dept, and customer"""
    
    # Read Excel data
    print("Reading Excel file...")
    archive_mapping = read_excel_data(excel_path)
    print(f"Found {len(archive_mapping)} archive ID mappings in Excel file")
    
    # Read results.csv and extract archive IDs
    print("Processing results.csv...")
    results_data = []
    
    try:
        with open(results_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                directory_name = row['Directory']
                archive_id = extract_archive_id(directory_name)
                
                if archive_id:
                    # Look up cost dept and customer
                    mapping = archive_mapping.get(archive_id, {'cost_dept': '', 'customer': ''})
                    
                    results_data.append({
                        'Archive_ID': archive_id,
                        'Cost_Dept': mapping['cost_dept'],
                        'Customer': mapping['customer'],
                        'Original_Directory': directory_name
                    })
    
    except Exception as e:
        print(f"Error reading results.csv: {e}")
        return
    
    # Write output CSV
    print(f"Writing output to {output_csv_path}...")
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Archive_ID', 'Cost_Dept', 'Customer', 'Original_Directory']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in results_data:
                writer.writerow(row)
        
        print(f"Successfully created {output_csv_path} with {len(results_data)} records")
        
        # Print summary
        matched_count = sum(1 for row in results_data if row['Cost_Dept'] or row['Customer'])
        print(f"Matched {matched_count} archive IDs with Excel data")
        print(f"Unmatched: {len(results_data) - matched_count}")
        
    except Exception as e:
        print(f"Error writing output CSV: {e}")

def main():
    # File paths
    current_dir = Path(__file__).parent
    results_csv_path = current_dir / 'results.csv'
    excel_path = Path(r'C:\Users\Ali\Desktop\micro\.utils\costdept\Auftragsüberwachung_ab_2016.xlsx')
    output_csv_path = current_dir / 'archive_mapping.csv'
    
    # Check if files exist
    if not results_csv_path.exists():
        print(f"Error: {results_csv_path} not found")
        return
    
    if not excel_path.exists():
        print(f"Error: {excel_path} not found")
        return
    
    # Process the files
    process_results_csv(results_csv_path, excel_path, output_csv_path)

if __name__ == "__main__":
    main()






