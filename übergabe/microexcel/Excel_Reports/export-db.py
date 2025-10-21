import openpyxl
import sqlite3
import pandas as pd

conn = sqlite3.connect(r'.\db.sqlite3')

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn) 

with pd.ExcelWriter("db-micr.xlsx", engine="openpyxl") as writer:
    used_names = set()
    for table in tables['name']:
        df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
        
        # Truncate sheet name to 31 characters and ensure uniqueness
        sheet_name = table[:31]
        counter = 1
        original_name = sheet_name
        while sheet_name in used_names:
            # If name is already used, add a counter
            suffix = f"_{counter}"
            max_length = 31 - len(suffix)
            sheet_name = original_name[:max_length] + suffix
            counter += 1
        
        used_names.add(sheet_name)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("DONE")