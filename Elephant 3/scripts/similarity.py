# import pandas as pd
# import numpy as np
# import os
# import matplotlib.pyplot as plt
# import seaborn as sns
# from datetime import datetime
# from collections import defaultdict
# import re
# from math import radians, sin, cos, sqrt, atan2

# # Haversine distance function
# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371.0
#     dlat = radians(lat2 - lat1)
#     dlon = radians(lon2 - lon1)
#     a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))
#     return R * c

# # Vectorized haversine
# def haversine_vectorized(lats1, lons1, lats2, lons2):
#     lats1_rad = np.radians(lats1)
#     lons1_rad = np.radians(lons1)
#     lats2_rad = np.radians(lats2)
#     lons2_rad = np.radians(lons2)
#     dlat = lats2_rad - lats1_rad
#     dlon = lons2_rad - lons1_rad
#     a = np.sin(dlat / 2)**2 + np.cos(lats1_rad) * np.cos(lats2_rad) * np.sin(dlon / 2)**2
#     c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
#     return 6371 * c

# def parse_filename(filename):
#     match = re.match(r'(\d+[fem]e)_([a-z_]+)_(\d{4})\.csv', filename, re.IGNORECASE)
#     if match:
#         ele_id, season_raw, year_str = match.groups()
#         season = season_raw.replace('_', ' ')
#         sex = 'F' if 'fe' in ele_id.lower() else 'M'
#         return {
#             'elephant_id': ele_id,
#             'season': season,
#             'year': int(year_str),
#             'sex': sex
#         }
#     return None

# def load_data(fe_path, me_path):
#     all_data = []
#     for folder, expected_sex in [(fe_path, 'F'), (me_path, 'M')]:
#         if not os.path.exists(folder):
#             print(f"Warning: Folder '{folder}' not found.")
#             continue
#         for filename in os.listdir(folder):
#             if filename.endswith('.csv'):
#                 parsed = parse_filename(filename)
#                 if parsed:
#                     filepath = os.path.join(folder, filename)
#                     df_temp = pd.read_csv(filepath)
#                     if 'DateTime' in df_temp.columns:
#                         df_temp['timestamp'] = pd.to_datetime(df_temp['DateTime'], errors='coerce')
#                     elif 'Date' in df_temp.columns and 'Time' in df_temp.columns:
#                         df_temp['timestamp'] = pd.to_datetime(df_temp['Date'].astype(str) + ' ' + df_temp['Time'].astype(str), errors='coerce')
#                     else:
#                         continue
#                     if 'Latitude' in df_temp.columns:
#                         df_temp['latitude'] = df_temp['Latitude']
#                     if 'Longitude' in df_temp.columns:
#                         df_temp['longitude'] = df_temp['Longitude']
#                     # Use parsed['elephant_id'] by default, or 'individual-local-identifier' if present
#                     if 'individual-local-identifier' in df_temp.columns:
#                         unique_id = df_temp['individual-local-identifier'].dropna().unique()
#                         df_temp['elephant_id'] = unique_id[0] if len(unique_id) == 1 else parsed['elephant_id']
#                     else:
#                         df_temp['elephant_id'] = parsed['elephant_id']
#                     df_temp['year'] = parsed['year']
#                     df_temp['season'] = parsed['season']
#                     df_temp['sex'] = parsed['sex']
#                     select_cols = ['elephant_id', 'sex', 'timestamp', 'latitude', 'longitude', 'season', 'year']
#                     available_cols = [col for col in select_cols if col in df_temp.columns]
#                     all_data.append(df_temp[available_cols])
#     if all_data:
#         df = pd.concat(all_data, ignore_index=True)
#         df = df.sort_values(['elephant_id', 'timestamp'])
#         df = df.dropna(subset=['timestamp', 'latitude', 'longitude'])
#         return df
#     else:
#         raise ValueError("No data files found.")

# # Change the following variables to your path structure:
# script_dir = os.path.dirname(os.path.abspath(__file__))
# data_dir = os.path.join(script_dir, '..', 'data')
# fe_folder = os.path.join(data_dir, 'fe')
# me_folder = os.path.join(data_dir, 'me')
# save_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Similarity"
# os.makedirs(save_dir, exist_ok=True)
# df = load_data(fe_folder, me_folder)

# # Resampling
# resampled_dfs = []
# for ele in df['elephant_id'].unique():
#     ele_df = df[df['elephant_id'] == ele].copy()
#     if len(ele_df) < 2:
#         continue
#     numeric_cols = ['latitude', 'longitude']
#     ele_numeric = ele_df.set_index('timestamp')[numeric_cols].resample('30min').median(numeric_only=True).reset_index()
#     ele_numeric['elephant_id'] = ele
#     ele_numeric['sex'] = ele_df['sex'].iloc[0]
#     ele_numeric['season'] = ele_df['season'].mode().iloc[0] if not ele_df['season'].mode().empty else ele_df['season'].iloc[0]
#     ele_numeric['year'] = ele_df['year'].mode().iloc[0] if not ele_df['year'].mode().empty else ele_df['year'].iloc[0]
#     ele_numeric = ele_numeric.dropna(subset=['latitude', 'longitude'])
#     resampled_dfs.append(ele_numeric)

# df = pd.concat(resampled_dfs, ignore_index=True)

# # FIXED: Co-location function uses real elephant_id strings
# def find_co_locations(df, dist_tolerance=0.1, time_tolerance='1h', max_obs_per_ele=500):
#     co_locs = []
#     elephants = sorted(df['elephant_id'].unique())
#     for i, ele1 in enumerate(elephants):
#         ele1_df = df[df['elephant_id'] == ele1].sort_values('timestamp').head(max_obs_per_ele)
#         for ele2 in elephants[i+1:]:
#             ele2_df = df[df['elephant_id'] == ele2].sort_values('timestamp').head(max_obs_per_ele)
#             if len(ele1_df) < 1 or len(ele2_df) < 1:
#                 continue

#             ele1_df_rename = ele1_df.rename(columns={
#                 'latitude': 'latitude_1',
#                 'longitude': 'longitude_1',
#                 'timestamp': 'timestamp_1',
#                 'year': 'year_1',
#                 'season': 'season_1'
#             })
#             ele2_df_rename = ele2_df.rename(columns={
#                 'latitude': 'latitude_2',
#                 'longitude': 'longitude_2',
#                 'timestamp': 'timestamp_2',
#                 'year': 'year_2',
#                 'season': 'season_2'
#             })

#             merged = pd.merge_asof(
#                 ele1_df_rename.sort_values('timestamp_1'),
#                 ele2_df_rename.sort_values('timestamp_2'),
#                 left_on='timestamp_1',
#                 right_on='timestamp_2',
#                 direction='nearest',
#                 tolerance=pd.Timedelta(time_tolerance)
#             )
#             merged = merged.dropna(subset=['latitude_1', 'latitude_2', 'timestamp_2'])
#             merged['time_diff'] = abs(merged['timestamp_1'] - merged['timestamp_2'])
#             time_mask = merged['time_diff'] <= pd.Timedelta(time_tolerance)
#             filtered = merged[time_mask]
#             if len(filtered) == 0:
#                 continue

#             dists = haversine_vectorized(
#                 filtered['latitude_1'], filtered['longitude_1'],
#                 filtered['latitude_2'], filtered['longitude_2']
#             )
#             close_mask = dists <= dist_tolerance
#             close_merged = filtered[close_mask]
#             for idx, row in close_merged.iterrows():
#                 co_locs.append({
#                     'elephant1': ele1,  # <-- always real ID, e.g. '01fe'
#                     'elephant2': ele2,
#                     'timestamp': min(row['timestamp_1'], row['timestamp_2']),
#                     'location': ((row['latitude_1'] + row['latitude_2']) / 2, (row['longitude_1'] + row['longitude_2']) / 2),
#                     'distance_km': dists[close_mask][close_merged.index - filtered.index[0]],
#                     'year': row['year_1'],
#                     'season': row['season_1']
#                 })
#     return pd.DataFrame(co_locs)

# co_locations = find_co_locations(df)
# co_locations[['elephant1', 'elephant2', 'timestamp', 'location', 'distance_km', 'year', 'season']].to_csv(os.path.join(save_dir, 'co_locations.csv'), index=False)
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
from math import radians, sin, cos, sqrt, atan2

# Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def haversine_vectorized(lats1, lons1, lats2, lons2):
    lats1_rad = np.radians(lats1)
    lons1_rad = np.radians(lons1)
    lats2_rad = np.radians(lats2)
    lons2_rad = np.radians(lons2)
    dlat = lats2_rad - lats1_rad
    dlon = lons2_rad - lons1_rad
    a = np.sin(dlat / 2)**2 + np.cos(lats1_rad) * np.cos(lats2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return 6371 * c

# Parse filename for IDs and metadata
def parse_filename(filename):
    match = re.match(r'(\d+[fem]e)_([a-z_]+)_(\d{4})\.csv', filename, re.IGNORECASE)
    if match:
        ele_id, season_raw, year_str = match.groups()
        season = season_raw.replace('_', ' ')
        sex = 'F' if 'fe' in ele_id.lower() else 'M'
        return {
            'elephant_id': ele_id,
            'season': season,
            'year': int(year_str),
            'sex': sex
        }
    return None

# Load female & male data, always setting elephant_id from parsed names or unique file content
def load_data(fe_path, me_path):
    all_data = []
    for folder, expected_sex in [(fe_path, 'F'), (me_path, 'M')]:
        if not os.path.exists(folder):
            print(f"Warning: Folder '{folder}' not found.")
            continue
        for filename in os.listdir(folder):
            if filename.endswith('.csv'):
                parsed = parse_filename(filename)
                if parsed:
                    filepath = os.path.join(folder, filename)
                    df_temp = pd.read_csv(filepath)
                    if 'DateTime' in df_temp.columns:
                        df_temp['timestamp'] = pd.to_datetime(df_temp['DateTime'], errors='coerce')
                    elif 'Date' in df_temp.columns and 'Time' in df_temp.columns:
                        df_temp['timestamp'] = pd.to_datetime(df_temp['Date'].astype(str) + ' ' + df_temp['Time'].astype(str), errors='coerce')
                    else:
                        continue
                    if 'Latitude' in df_temp.columns:
                        df_temp['latitude'] = df_temp['Latitude']
                    if 'Longitude' in df_temp.columns:
                        df_temp['longitude'] = df_temp['Longitude']
                    if 'individual-local-identifier' in df_temp.columns:
                        unique_id = df_temp['individual-local-identifier'].dropna().unique()
                        df_temp['elephant_id'] = unique_id[0] if len(unique_id) == 1 else parsed['elephant_id']
                    else:
                        df_temp['elephant_id'] = parsed['elephant_id']
                    df_temp['year'] = parsed['year']
                    df_temp['season'] = parsed['season']
                    df_temp['sex'] = parsed['sex']
                    select_cols = ['elephant_id', 'sex', 'timestamp', 'latitude', 'longitude', 'season', 'year']
                    available_cols = [col for col in select_cols if col in df_temp.columns]
                    all_data.append(df_temp[available_cols])
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        df = df.sort_values(['elephant_id', 'timestamp'])
        df = df.dropna(subset=['timestamp', 'latitude', 'longitude'])
        return df
    else:
        raise ValueError("No data files found.")

# Change to your folder paths as needed!
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', 'data')
fe_folder = os.path.join(data_dir, 'fe')
me_folder = os.path.join(data_dir, 'me')
save_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Similarity"
os.makedirs(save_dir, exist_ok=True)
df = load_data(fe_folder, me_folder)

# Resample
resampled_dfs = []
for ele in df['elephant_id'].unique():
    ele_df = df[df['elephant_id'] == ele].copy()
    if len(ele_df) < 2:
        continue
    numeric_cols = ['latitude', 'longitude']
    ele_numeric = ele_df.set_index('timestamp')[numeric_cols].resample('30min').median(numeric_only=True).reset_index()
    ele_numeric['elephant_id'] = ele
    ele_numeric['sex'] = ele_df['sex'].iloc[0]
    ele_numeric['season'] = ele_df['season'].mode().iloc[0] if not ele_df['season'].mode().empty else ele_df['season'].iloc[0]
    ele_numeric['year'] = ele_df['year'].mode().iloc[0] if not ele_df['year'].mode().empty else ele_df['year'].iloc[0]
    ele_numeric = ele_numeric.dropna(subset=['latitude', 'longitude'])
    resampled_dfs.append(ele_numeric)

df = pd.concat(resampled_dfs, ignore_index=True)

# Main: co-location using actual elephant IDs
def find_co_locations(df, dist_tolerance=0.1, time_tolerance='1h', max_obs_per_ele=500):
    co_locs = []
    elephants = sorted(df['elephant_id'].unique())
    for i, ele1 in enumerate(elephants):
        ele1_df = df[df['elephant_id'] == ele1].sort_values('timestamp').head(max_obs_per_ele)
        for ele2 in elephants[i+1:]:
            ele2_df = df[df['elephant_id'] == ele2].sort_values('timestamp').head(max_obs_per_ele)
            if len(ele1_df) < 1 or len(ele2_df) < 1:
                continue
            ele1_df_rename = ele1_df.rename(columns={
                'latitude': 'latitude_1', 'longitude': 'longitude_1', 'timestamp': 'timestamp_1',
                'year': 'year_1', 'season': 'season_1'
            })
            ele2_df_rename = ele2_df.rename(columns={
                'latitude': 'latitude_2', 'longitude': 'longitude_2', 'timestamp': 'timestamp_2',
                'year': 'year_2', 'season': 'season_2'
            })
            merged = pd.merge_asof(
                ele1_df_rename.sort_values('timestamp_1'),
                ele2_df_rename.sort_values('timestamp_2'),
                left_on='timestamp_1',
                right_on='timestamp_2',
                direction='nearest',
                tolerance=pd.Timedelta(time_tolerance)
            ).dropna(subset=['latitude_1', 'latitude_2', 'timestamp_2'])

            merged['time_diff'] = abs(merged['timestamp_1'] - merged['timestamp_2'])
            time_mask = merged['time_diff'] <= pd.Timedelta(time_tolerance)
            filtered = merged[time_mask]
            if len(filtered) == 0:
                continue

            dists = haversine_vectorized(
                filtered['latitude_1'], filtered['longitude_1'],
                filtered['latitude_2'], filtered['longitude_2']
            )
            close_mask = dists <= dist_tolerance
            close_merged = filtered[close_mask]
            for idx, row in close_merged.iterrows():
                co_locs.append({
                    'elephant1': ele1,  # never LA1!
                    'elephant2': ele2,  # never LA2!
                    'timestamp': min(row['timestamp_1'], row['timestamp_2']),
                    'location': ((row['latitude_1'] + row['latitude_2']) / 2, (row['longitude_1'] + row['longitude_2']) / 2),
                    'distance_km': dists[close_mask][close_merged.index - filtered.index[0]],
                    'year': row['year_1'],
                    'season': row['season_1']
                })
    return pd.DataFrame(co_locs)

co_locations = find_co_locations(df)
co_locations[['elephant1', 'elephant2', 'timestamp', 'location', 'distance_km', 'year', 'season']].to_csv(os.path.join(save_dir, 'co_locations.csv'), index=False)
print(co_locations[['elephant1', 'elephant2']].head())
