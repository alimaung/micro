import re 
import xlwings as xw

def extract_xlsx():
    # Open the workbook
    wb = xw.Book('RRD095-2024_ComList.xlsx')
    sheet = wb.sheets[0]  # Tabelle 1/ Sheet 1

    # List to store extracted barcode data
    barcode_data = []
    
    last_row = sheet.range("A" + str(sheet.cells.last_cell.row)).end('up').row  # Find last filled row
    
    for row in range(1, last_row + 1):  # Start from row 1 (no headers)
        barcode = str(sheet.range(f"A{row}").value).strip()  # Read barcode
        com_id = str(sheet.range(f"B{row}").value).strip()  # Read com_id

        if barcode and com_id:
            barcode_data.append({
                "barcode": barcode,
                "com_id": com_id
            })
            
    return barcode_data 

def extract_txt():
    # Open the file with the correct encoding
    with open('430179.txt', 'r', encoding='utf-16le') as f:
        lines = f.readlines()  # Read all lines into a list

    data = {} # Dictionary to store metadata
    barcode_data = [] # List to store extracted barcode data

    # Process lines one by one
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace

        # Extract metadata
        if "Rollennummer=" in line:
            data["roll"] = line.split("=")[1]

        # Extract barcode details from subsequent lines
        elif re.match(r'^\d+\.pdf;', line):  # Matches lines with PDF filenames
            parts = line.split(";")
            filename = parts[0]  # Full filename
            barcode = filename.split(".")[0]  # Extract barcode (without .pdf)
            blip = parts[1]  # Blip value

            # Store data as a dictionary
            barcode_data.append({
                "barcode": barcode,
                "blip": blip
            })
    return data, barcode_data 

def process_txt(data, barcode_data):
    text = []
    for entry in barcode_data:
        entry.update(data)
        text.append(entry)    
    return text

def combine_data(excel_data, txt_data):
    # Create a dictionary from the Excel data using barcode as the key
    excel_dict = {entry["barcode"]: entry["com_id"] for entry in excel_data}
    
    # Iterate over the txt_data and add the corresponding com_id if available
    combined_data = []
    for entry in txt_data:
        barcode = entry["barcode"]
        if barcode in excel_dict:
            entry["com_id"] = excel_dict[barcode]  # Add com_id to the entry
        combined_data.append(entry)
    
    #print(f"\033[34m{combined_data}\033[0m")
    return combined_data

def process_blips(data):
    # Initialize variables
    result = []
    total_pages = 0
    
    # Group data by barcode to count pages per document
    barcode_groups = {}
    for item in data:
        barcode = item['barcode']
        if barcode not in barcode_groups:
            barcode_groups[barcode] = []
        barcode_groups[barcode].append(item)
    
    # Process each document
    for barcode, items in barcode_groups.items():
        first_item = items[0] # Get the first item (first page) of the document
        doc_num = int(first_item['blip'].split('-')[1]) # Parse the current blip
        new_blip = f"0-{doc_num}-{total_pages + 1}" # Create new blip with continuous page numbering
        new_item = first_item.copy()# Create new dictionary with updated blip
        new_item['blip'] = new_blip
        result.append(new_item) # Add to result
        total_pages += len(items) # Update total pages counter
    return result

def convert(barcode_data):
    output_lines = []
    for entry in barcode_data:
        barcode = entry.get("barcode", "")
        com_id = entry.get("com_id", "")
        roll = entry.get("roll", "")
        blip = entry.get("blip", "")
        
        # Convert blip format
        blip_parts = blip.split('-')
        if len(blip_parts) == 3:
            blip_formatted = f"{int(blip_parts[0])}.{int(blip_parts[1]):04}.{int(blip_parts[2]):05}"
        else:
            blip_formatted = ""
        roll_blip = f"{roll}-{blip_formatted}" # Create roll-blip
        
        # Format scan.dat line
        line = f"{barcode:<21}{com_id:<40}{roll_blip}"
        output_lines.append(line)
    
    # Save to scan.dat
    with open("scan1.dat", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    print("\033[35mSaved scan.dat successfully\033[0m")

d = extract_xlsx()
m, t = extract_txt()
p = process_txt(m, t)
c = combine_data(d, p)
b = process_blips(c)
convert(b)