import os
import pandas as pd
import numpy as np

# Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "segments")
NSD_OUTPUT_DIR = os.path.join(BASE_DIR, "..", "nsd")

os.makedirs(NSD_OUTPUT_DIR, exist_ok=True)

def calculate_nsd(df):
    """Calculate Net Squared Displacement from the first point of the dataframe."""
    if df.empty:
        return df
    first_lon, first_lat = df.iloc[0]['Longitude'], df.iloc[0]['Latitude']
    # Euclidean squared distance: (Δx² + Δy²)
    df['nsd'] = (df['Longitude'] - first_lon)**2 + (df['Latitude'] - first_lat)**2
    #df['displacement'] = np.sqrt((df['Longitude'] - first_lon)**2 + (df['Latitude'] - first_lat)**2)
    return df

# Process Groups
for group in ["fe", "me"]:
    group_dir = os.path.join(SEGMENTS_DIR, group)
    if not os.path.exists(group_dir):
        continue
        
    # Create subfolders in nsd directory to maintain structure
    save_path = os.path.join(NSD_OUTPUT_DIR, group)
    os.makedirs(save_path, exist_ok=True)

    for file in sorted(os.listdir(group_dir)):
        if file.endswith(".csv"):
            file_path = os.path.join(group_dir, file)
            
            # Load, Calculate, and Save
            df = pd.read_csv(file_path)
            df = calculate_nsd(df)
            
            output_file = os.path.join(save_path, file)
            df.to_csv(output_file, index=False)
            print(f"Saved NSD data to: {output_file}")