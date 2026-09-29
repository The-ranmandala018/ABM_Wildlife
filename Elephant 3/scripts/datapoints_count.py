import os
import pandas as pd
from datetime import datetime
import glob

# Define paths
data_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\fe'
output_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
output_file = os.path.join(output_dir, 'elephant_daily_counts_fe.csv')

# Find all CSV files in data directory and its subdirectories (e.g., fe, me)
csv_files = glob.glob(os.path.join(data_dir, '**/*.csv'), recursive=True)

# Required columns for elephant data (no longer including 'individual-local-identifier')
required_cols = ['DateTime', 'Longitude', 'Latitude']

# List to hold all processed data
all_counts = []

for file_path in csv_files:
    print(f"Processing {os.path.basename(file_path)} from {os.path.dirname(file_path)}")
    
    try:
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        if not all(col in df.columns for col in required_cols):
            print(f"  Skipping: Missing required columns {required_cols}")
            continue
        
        # Extract elephant_name from filename (e.g., '01fe' from '01fe_cold_dry_2009.csv')
        filename = os.path.basename(file_path)
        elephant_name = filename.split('_')[0]  # Assumes format like '01fe_cold_dry_2009.csv'
        
        # Parse DateTime to datetime
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        
        # Extract year and date (day)
        df['year'] = df['DateTime'].dt.year
        df['day'] = df['DateTime'].dt.date
        
        # Filter rows with valid lon/lat (non-null)
        df = df.dropna(subset=['Longitude', 'Latitude'])
        # Optional: Add bounds check
        # df = df[(df['Longitude'] >= -180) & (df['Longitude'] <= 180) & 
        #         (df['Latitude'] >= -90) & (df['Latitude'] <= 90)]
        
        # Group by year, day and count (one elephant per file)
        counts = df.groupby(['year', 'day']).size().reset_index(name='count')
        
        # Add elephant_name (from filename)
        counts['elephant_name'] = elephant_name
        
        # Add file name for reference
        counts['file'] = filename
        # Add subfolder for reference (e.g., 'fe' or 'me')
        subfolder = os.path.basename(os.path.dirname(file_path))
        counts['subfolder'] = subfolder
        
        all_counts.append(counts)
        print(f"  Processed: {len(counts)} records for {elephant_name}")
        
    except Exception as e:
        print(f"  Error processing: {e}")
        continue

# Concatenate all
if all_counts:
    combined = pd.concat(all_counts, ignore_index=True)
    
    # Sort for better readability
    combined = combined.sort_values(['elephant_name', 'year', 'day'])
    
    # Save to CSV
    combined.to_csv(output_file, index=False)
    print(f"Output saved to {output_file}")
    
    # Display summary
    print("\nSummary:")
    print(combined.head())
    print(f"\nTotal records: {len(combined)}")
    print(f"Unique elephants: {combined['elephant_name'].nunique()}")
    print(f"Sample elephant names: {sorted(combined['elephant_name'].unique())[:5]}...")
else:
    print("No valid CSV files with required columns found.")