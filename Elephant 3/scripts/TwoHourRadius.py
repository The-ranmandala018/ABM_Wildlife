import pandas as pd
import numpy as np
import os
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of earth in kilometers
    return c * r * 1000  # meters

# Input and output directories
input_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\clusters\fe"
output_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Resting"
filename = "03fe_hot_wet_eps50minPTS50_ClusterData.csv"
file_path = os.path.join(input_dir, filename)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the CSV (preserves all original columns)
df = pd.read_csv(file_path)

# Create DateTime column for easier handling (does not modify original columns)
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

# Year variable
year = 2011

# Filter for the specific year
df_year = df[df['DateTime'].dt.year == year].copy().reset_index(drop=True)

# Find resting periods: sequences of at least 7 consecutive points (120+ min, ~2 hours at 20-min intervals)
# where all points are within 10m radius of the centroid
resting_events = []
n = len(df_year)
for i in range(n - 6):
    window = df_year.iloc[i:i+7]
    if len(window) < 7:
        continue
    lats = window['Latitude'].values
    lons = window['Longitude'].values
    centroid_lat = np.mean(lats)
    centroid_lon = np.mean(lons)
    dists = [haversine(centroid_lon, centroid_lat, lon, lat) for lon, lat in zip(lons, lats)]
    max_dist = max(dists)
    start_time = window.iloc[0]['DateTime']
    end_time = window.iloc[-1]['DateTime']
    duration_hours = (end_time - start_time).total_seconds() / 3600
    if max_dist <= 10 and duration_hours >= 2:
        resting_events.append({
            'Year': year,
            'Resting_Latitude': round(centroid_lat, 8),
            'Resting_Longitude': round(centroid_lon, 8),
            'Start_DateTime': start_time,
            'End_DateTime': end_time,
            'Duration_Hours': round(duration_hours, 2),
            'Individual': window.iloc[0]['individual-local-identifier'],
            'Season': window.iloc[0]['Season']
        })

# Create output DataFrame
if resting_events:
    resting_df = pd.DataFrame(resting_events)
    output_filename = f"resting_locations_{year}.csv"
    output_path = os.path.join(output_dir, output_filename)
    resting_df.to_csv(output_path, index=False)
    print(f"Resting locations saved to: {output_path}")
    print(f"Found {len(resting_events)} resting periods.")
else:
    print(f"No resting periods found for year {year}.")