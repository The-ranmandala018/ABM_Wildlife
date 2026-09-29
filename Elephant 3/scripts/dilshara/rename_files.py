import pandas as pd
from datetime import datetime
import glob
import os

if __name__ == "__main__":
    class_names = ["af", "am", "jm", "sf", "sm"]
    
    for class_name in class_names:
        # Define the path pattern for CSV files in the class folder
        path_pattern = f"../../data/{class_name}/*.csv"
        
        # Get list of all CSV files matching the pattern
        csv_files = sorted(glob.glob(path_pattern))  # Sort for consistent order
        
        if not csv_files:
            print(f"No CSV files found in {path_pattern}")
        else:
            print(f"Found {len(csv_files)} CSV files to process in {class_name} folder")
            
            # Process each CSV file for renaming
            for index, csv_file in enumerate(csv_files, start=1):
                # Generate new filename with two-digit prefix
                new_filename = f"{index:02d}{class_name}.csv"
                # Construct full path for new filename
                new_filepath = os.path.join(os.path.dirname(csv_file), new_filename)
                
                try:
                    # Rename the file
                    os.rename(csv_file, new_filepath)
                    print(f"Renamed {csv_file} to {new_filepath}")
                except OSError as e:
                    print(f"Error renaming {csv_file} to {new_filepath}: {e}")