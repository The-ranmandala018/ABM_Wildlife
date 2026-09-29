import pandas as pd
import os
from datetime import datetime

# Input and output directories (absolute paths as provided)
input_base_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data"
output_base_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Filter_By_Year"

# Ensure output base directory exists
os.makedirs(output_base_dir, exist_ok=True)

# Subfolders to process (e.g., 'fe', 'me')
subfolders = ['fe', 'me']  # Add more if needed

for subfolder in subfolders:
    input_subdir = os.path.join(input_base_dir, subfolder)
    output_subdir = os.path.join(output_base_dir, subfolder)
    
    # Ensure output subdir exists
    os.makedirs(output_subdir, exist_ok=True)
    
    if not os.path.exists(input_subdir):
        print(f"Subfolder {input_subdir} does not exist. Skipping.")
        continue
    
    # Find all CSV files in the subfolder
    csv_files = [f for f in os.listdir(input_subdir) if f.endswith('.csv')]
    
    for csv_file in csv_files:
        file_path = os.path.join(input_subdir, csv_file)
        print(f"Processing {file_path}...")
        
        # Load the CSV
        df = pd.read_csv(file_path)
        
        # Create DateTime column (assuming 'Date' and 'Time' columns exist)
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        
        # Group by year and save each year's data
        years = df['DateTime'].dt.year.unique()
        for year in sorted(years):
            df_year = df[df['DateTime'].dt.year == year].copy()
            
            if not df_year.empty:
                # Extract base name without .csv
                base_name = csv_file.replace('.csv', '')
                output_filename = f"{base_name}_{year}.csv"
                output_file = os.path.join(output_subdir, output_filename)
                df_year.to_csv(output_file, index=False)
                print(f"Saved year {year} data to {output_file} ({len(df_year)} rows).")
        
        print(f"Finished processing {csv_file}.")

print("All files processed.")