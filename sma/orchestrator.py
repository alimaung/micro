import sma
import argparse
import os
import lock

def process_folder(folder_path, template="16", filmnumber=None, recovery=False):
    """Process a single folder using sma.main"""
    args = argparse.Namespace()
    args.folder_path = folder_path
    args.template = template
    args.filmnumber = filmnumber
    args.recovery = recovery
    
    print(f"Processing folder: {folder_path}")
    sma.main(args)
    print(f"Completed processing folder: {folder_path}")


#output_path = r"F:\microfilm+\microfilm\testing\RRD017-2024_OU_GROSS\.output"
#output_dir = os.listdir(output_path)
#
## Process each folder
#for folder in output_dir:
#    folder_path = os.path.join(output_path, folder)
#    process_folder(folder_path, template="16")