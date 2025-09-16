import openpyxl
import sqlite3
import pandas as pd

conn = sqlite3.connect('.\db.sqlite3')

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn) 

with pd.ExcelWriter("db.xlsx", engine="openpyxl") as writer:
    for table in tables['name']:
        df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
        df.to_excel(writer, sheet_name=table, index=False)

print("DONE")