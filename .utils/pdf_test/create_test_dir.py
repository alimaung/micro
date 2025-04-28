# construct list of 20 more or less random"foldernames" with regex pattern: RRDXXX-YYYY_OU_DOCTYPE XXX- number, YYYY random year (2000- 2025), OU - location code, either DW or OU, DOCTYPE - some random document types
# e.g. RRD001-2024_OU_Q3REPORT, RRD002-2024_OU_INVOICE, RRD003-2024_DW_DATASHEET
# create a list of 10 random document types and assign them to the foldernames randomly
# groups seperated by _ 
# start with XXX : 001, choose OU or DW randomly, then choose a random year between 2000 and 2025, then choose a random document type
# then create a folder for each name in the list in Y:

import random
import os
from datetime import datetime

# List of document types
DOC_TYPES = [
    'Q1REPORT', 'Q2REPORT', 'Q3REPORT', 'Q4REPORT',
    'INVOICE', 'DATASHEET', 'CONTRACT', 'MEMO',
    'PROPOSAL', 'BUDGET'
]

# List to store folder names
folder_names = []

# Generate 20 folder names
for i in range(1, 21):
    # Format number with leading zeros
    number = str(i).zfill(3)
    
    # Random year between 2000 and 2025
    year = random.randint(2000, 2025)
    
    # Random location (OU or DW)
    location = random.choice(['OU', 'DW'])
    
    # Random document type
    doc_type = random.choice(DOC_TYPES)
    
    # Create folder name in the format: RRDXXX-YYYY_OU_DOCTYPE
    folder_name = f"RRD{number}-{year}_{location}_{doc_type}"
    folder_names.append(folder_name)

# Create folders in Y: drive
base_path = "Y:"
if not os.path.exists(base_path):
    print(f"Warning: {base_path} does not exist. Creating folders in current directory instead.")
    base_path = "."

# Create folders
for folder_name in folder_names:
    folder_path = os.path.join(base_path, folder_name)
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created folder: {folder_path}")
    except Exception as e:
        print(f"Error creating folder {folder_path}: {e}")

print("\nFolder names generated:")
for name in folder_names:
    print(name)

