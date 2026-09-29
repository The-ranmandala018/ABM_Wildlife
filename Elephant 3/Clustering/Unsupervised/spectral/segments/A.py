import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import os
import glob

# Directory with input files
input_dir = r"D:\Documents\MARC\Elephant\ai4covid_clustering-dev\data\me"

# Find all CSV files matching *fe*.csv pattern
files = glob.glob(os.path.join(input_dir, "*me*.csv"))

# Function to calculate haversine distance
def haversine(lon1, lat1, lon2, lat2):
    R = 6371000  # Earth radius in meters
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# Function to calculate bearing
def bearing(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    initial_bearing = atan2(x, y)
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

# Process each file
for file in files:
    print(f"Processing {file}...")
    
    # Read the file
    df = pd.read_csv(file)
    
    # Handle DateTime if present, or create from Date and timeAPM
    if 'DateTime' not in df.columns:
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['timeAPM'])
    else:
        df['DateTime'] = pd.to_datetime(df['DateTime'])
    
    # Sort by DateTime
    df = df.sort_values('DateTime').reset_index(drop=True)
    
    # Add geometry column
    df['geometry'] = 'POINT (' + df['Longitude'].astype(str) + ' ' + df['Latitude'].astype(str) + ')'
    
    # Calculate step_length, dt_sec, speed, bearing, turning_angle
    df['step_length'] = np.nan
    df['dt_sec'] = np.nan
    df['speed'] = np.nan
    df['bearing'] = np.nan
    df['turning_angle'] = np.nan
    
    for i in range(1, len(df)):
        lon1, lat1 = df.loc[i-1, 'Longitude'], df.loc[i-1, 'Latitude']
        lon2, lat2 = df.loc[i, 'Longitude'], df.loc[i, 'Latitude']
        dt = (df.loc[i, 'DateTime'] - df.loc[i-1, 'DateTime']).total_seconds()
        
        if dt > 0:
            dist = haversine(lon1, lat1, lon2, lat2)
            df.loc[i, 'step_length'] = dist
            df.loc[i, 'dt_sec'] = dt
            df.loc[i, 'speed'] = dist / dt if dt > 0 else 0
            df.loc[i, 'bearing'] = bearing(lon1, lat1, lon2, lat2)
            
            if i > 1:
                prev_bearing = df.loc[i-1, 'bearing']
                curr_bearing = df.loc[i, 'bearing']
                turning = curr_bearing - prev_bearing
                turning = (turning + 180) % 360 - 180  # Normalize to -180 to 180
                df.loc[i, 'turning_angle'] = turning
    
    # Residence time - assuming it's 0 if moving, or dt if step small (threshold e.g. 10m)
    threshold = 10  # meters
    df['residence_time'] = 0
    for i in range(1, len(df)):
        if df.loc[i, 'step_length'] < threshold:
            df.loc[i, 'residence_time'] = df.loc[i, 'dt_sec']
        else:
            df.loc[i, 'residence_time'] = 0
    
    # Reorder columns to match example (adjust if Season present)
    columns = ['Longitude', 'Latitude', 'individual-local-identifier', 'Date', 'timeAPM', 'Time']
    if 'Season' in df.columns:
        columns.append('Season')
    columns.extend(['datetime', 'geometry', 'step_length', 'dt_sec', 'speed', 'residence_time', 'bearing', 'turning_angle'])
    df['datetime'] = df['DateTime'].dt.strftime('%m/%d/%Y %H:%M')  # Match format
    df = df[columns]
    
    # Output filename
    base_name = os.path.basename(file).replace('.csv', '_with_segments.csv')
    output_path = os.path.join(input_dir, base_name)
    df.to_csv(output_path, index=False)
    print(f"Saved {output_path}")