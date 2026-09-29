# # Required installs: pip install ruptures pandas scikit-learn
# import pandas as pd
# import numpy as np
# import glob
# import os
# from ruptures import Binseg
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans

# def load_weather_data(halali_path, okaukuejo_path):
#     df_halali = pd.read_csv(halali_path)
#     df_okau = pd.read_csv(okaukuejo_path)
#     df_halali['Region'] = 'Halali'
#     df_okau['Region'] = 'Okaukuejo'
#     return pd.concat([df_halali, df_okau], ignore_index=True)

# def load_behavior_data(fe_path, me_path, max_files=None):  # Default to None (load all)
#     print(f"Loading behavior data from {fe_path} and {me_path} (max {max_files} files per sex)...")
   
#     # Load females
#     fe_files = glob.glob(os.path.join(fe_path, "*.csv"))
#     if not fe_files:
#         raise ValueError(f"No CSV files found in {fe_path}")
#     num_fe = len(fe_files) if max_files is None else min(max_files, len(fe_files))
#     print(f"Found {len(fe_files)} female files. Loading first {num_fe}...")
#     df_fe_list = []
#     for i, f in enumerate(fe_files[:num_fe], 1):
#         try:
#             print(f"  Loading female file {i}/{num_fe}: {os.path.basename(f)}")
#             df_temp = pd.read_csv(f, parse_dates=['Date'])
#             # Extract Elephant_ID from filename (e.g., "01fe" from "01fe_cold_dry_2009_08.csv")
#             filename = os.path.basename(f).replace('.csv', '')
#             elephant_id = filename.split('_')[0]
#             df_temp['Elephant_ID'] = elephant_id
#             df_fe_list.append(df_temp)
#             print(f"    -> Loaded {len(df_temp)} rows for {elephant_id}")
#         except Exception as e:
#             print(f"    -> Skipped due to error: {e}")
#     df_fe = pd.concat(df_fe_list, ignore_index=True) if df_fe_list else pd.DataFrame()
#     df_fe['Sex'] = 'Female'
#     print(f"Total female rows: {len(df_fe)}")
#     print(f"Unique female elephants: {sorted(df_fe['Elephant_ID'].unique())}")
   
#     # Load males
#     me_files = glob.glob(os.path.join(me_path, "*.csv"))
#     if not me_files:
#         raise ValueError(f"No CSV files found in {me_path}")
#     num_me = len(me_files) if max_files is None else min(max_files, len(me_files))
#     print(f"Found {len(me_files)} male files. Loading first {num_me}...")
#     df_me_list = []
#     for i, f in enumerate(me_files[:num_me], 1):
#         try:
#             print(f"  Loading male file {i}/{num_me}: {os.path.basename(f)}")
#             df_temp = pd.read_csv(f, parse_dates=['Date'])
#             # Extract Elephant_ID from filename (e.g., "01me" from "01me_cold_dry_2009_08.csv")
#             filename = os.path.basename(f).replace('.csv', '')
#             elephant_id = filename.split('_')[0]
#             df_temp['Elephant_ID'] = elephant_id
#             df_me_list.append(df_temp)
#             print(f"    -> Loaded {len(df_temp)} rows for {elephant_id}")
#         except Exception as e:
#             print(f"    -> Skipped due to error: {e}")
#     df_me = pd.concat(df_me_list, ignore_index=True) if df_me_list else pd.DataFrame()
#     df_me['Sex'] = 'Male'
#     print(f"Total male rows: {len(df_me)}")
#     print(f"Unique male elephants: {sorted(df_me['Elephant_ID'].unique())}")
   
#     combined = pd.concat([df_fe, df_me], ignore_index=True)
#     print(f"Combined behavior data: {len(combined)} rows, {len(combined.columns)} columns")
#     print(f"Sample columns: {list(combined.columns[:5])}")  # First 5 cols for sanity check
#     return combined

# def merge_data(weather_df, behavior_df):
#     weather_df['Date'] = pd.to_datetime(weather_df['Date'])
#     behavior_df['Date'] = pd.to_datetime(behavior_df['Date'])
#     merged = pd.merge_asof(behavior_df.sort_values('Date'),
#                            weather_df.sort_values('Date'),
#                            on='Date', direction='nearest')
#     return merged

# def detect_change_points(df, features, penalty=20):
#     # Filter to numeric features only (skip categoricals like 'Season')
#     numeric_features = [f for f in features if df[f].dtype in ['int64', 'float64'] and f in df.columns]
#     if len(numeric_features) < 2:
#         raise ValueError(f"Not enough numeric features for change-point detection. Available: {numeric_features}")
    
#     scaler = StandardScaler()
#     X = scaler.fit_transform(df[numeric_features])
#     algo = Binseg(model="l2").fit(X)
#     change_pts = algo.predict(pen=penalty)
#     return change_pts

# def assign_segments(df, change_pts):
#     segment_ids = np.zeros(len(df), dtype=int)
#     last = 0
#     for i, idx in enumerate(change_pts):
#         segment_ids[last:idx] = i
#         last = idx
#     segment_ids[last:] = len(change_pts)  # Assign last segment
#     df['Segment'] = segment_ids
#     return df

# def cluster_segments(df, features, n_clusters=3):
#     # Filter to numeric features only
#     numeric_features = [f for f in features if df[f].dtype in ['int64', 'float64'] and f in df.columns]
#     if len(numeric_features) < 1:
#         raise ValueError(f"No numeric features for clustering. Available: {numeric_features}")
    
#     segment_stats = df.groupby('Segment')[numeric_features].mean()
#     if len(segment_stats) < n_clusters:
#         print(f"Warning: Only {len(segment_stats)} segments found, but n_clusters={n_clusters}. Adjusting to {len(segment_stats)}.")
#         n_clusters = len(segment_stats)
    
#     scaler = StandardScaler()
#     X = scaler.fit_transform(segment_stats)
#     kmeans = KMeans(n_clusters=n_clusters, random_state=42)
#     segment_stats['Cluster'] = kmeans.fit_predict(X)
#     return segment_stats[['Cluster']]

# def main():
#     print("Starting main...")  # Confirm launch
   
#     halali_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/halali_weather_all_years.csv"
#     okaukuejo_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/okaukuejo_weather_all_years.csv"
#     fe_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/fe"
#     me_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/me"
#     base_out_dir = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/Clustering"
   
#     print("Loading weather data...")
#     weather_df = load_weather_data(halali_path, okaukuejo_path)
#     print(f"Weather loaded: {len(weather_df)} rows")
   
#     print("Loading behavior data (full load: no file limit)...")
#     behavior_df = load_behavior_data(fe_path, me_path, max_files=None)  # Load all files
   
#     print("Merging data...")
#     merged_df = merge_data(weather_df, behavior_df)
#     print(f"Merged: {len(merged_df)} rows")
   
#     features = ['Temp_C','Dew_C','Humidity_%','Wind_Kph','Press_Hg','Precip_mm','Longitude','Latitude','Season']
#     features = [f for f in features if f in merged_df.columns]
#     print(f"Using features: {features}")
    
#     # Extract Year from Date
#     merged_df['Year'] = merged_df['Date'].dt.year
    
#     # Cluster separately for each Elephant_ID and Year
#     print("Clustering separately for each elephant and year...")
#     groups = merged_df.groupby(['Elephant_ID', 'Year'])
#     print(f"Total groups to process: {len(groups)}")
#     for i, ((elephant_id, year), group) in enumerate(groups, 1):
#         if len(group) < 10:  # Skip very small groups
#             print(f"  [{i}/{len(groups)}] Skipping {elephant_id}_{year}: too few rows ({len(group)})")
#             continue
        
#         print(f"  [{i}/{len(groups)}] Processing {elephant_id}_{year} ({len(group)} rows)...")
#         group_features = [f for f in features if f in group.columns]
        
#         print("    Detecting change points...")
#         change_pts = detect_change_points(group, group_features, penalty=40)
#         print(f"    Change points: {change_pts}")
        
#         print("    Assigning segments...")
#         group = assign_segments(group, change_pts)
        
#         print("    Clustering segments...")
#         segment_clusters = cluster_segments(group, group_features, n_clusters=3)
        
#         print("    Merging clusters...")
#         group = group.merge(segment_clusters, left_on='Segment', right_index=True, how='left')
        
#         # Save to separate CSV
#         out_file = os.path.join(base_out_dir, f"clustered_segments_{elephant_id}_{year}.csv")
#         os.makedirs(base_out_dir, exist_ok=True)
#         group.to_csv(out_file, index=False)
#         print(f"    Saved: {out_file}")
    
#     print("All processing complete!")

# if __name__ == "__main__":
#     main()

# Segment using variance-based change-point detection
# import pandas as pd
# import numpy as np
# import glob
# import os
# from sklearn.preprocessing import StandardScaler
# import matplotlib.pyplot as plt  # For plotting
# import matplotlib.cm as cm  # For colormaps
# from datetime import datetime
# from geopy.distance import geodesic
# from itertools import groupby

# def load_weather_data(halali_path, okaukuejo_path):
#     df_halali = pd.read_csv(halali_path)
#     df_okau = pd.read_csv(okaukuejo_path)
#     df_halali['Region'] = 'Halali'
#     df_okau['Region'] = 'Okaukuejo'
#     return pd.concat([df_halali, df_okau], ignore_index=True)

# def load_behavior_data(fe_path, me_path, max_files=None):  # Default to None (load all)
#     print(f"Loading behavior data from {fe_path} and {me_path} (max {max_files} files per sex)...")
   
#     # Load females
#     fe_files = glob.glob(os.path.join(fe_path, "*.csv"))
#     if not fe_files:
#         raise ValueError(f"No CSV files found in {fe_path}")
#     num_fe = len(fe_files) if max_files is None else min(max_files, len(fe_files))
#     print(f"Found {len(fe_files)} female files. Loading first {num_fe}...")
#     df_fe_list = []
#     for i, f in enumerate(fe_files[:num_fe], 1):
#         try:
#             print(f"  Loading female file {i}/{num_fe}: {os.path.basename(f)}")
#             df_temp = pd.read_csv(f, parse_dates=['Date'])
#             # Extract Elephant_ID from filename (e.g., "01fe" from "01fe_cold_dry_2009_08.csv")
#             filename = os.path.basename(f).replace('.csv', '')
#             elephant_id = filename.split('_')[0]
#             df_temp['Elephant_ID'] = elephant_id
#             df_fe_list.append(df_temp)
#             print(f"    -> Loaded {len(df_temp)} rows for {elephant_id}")
#         except Exception as e:
#             print(f"    -> Skipped due to error: {e}")
#     df_fe = pd.concat(df_fe_list, ignore_index=True) if df_fe_list else pd.DataFrame()
#     df_fe['Sex'] = 'Female'
#     print(f"Total female rows: {len(df_fe)}")
#     print(f"Unique female elephants: {sorted(df_fe['Elephant_ID'].unique())}")
   
#     # Load males
#     me_files = glob.glob(os.path.join(me_path, "*.csv"))
#     if not me_files:
#         raise ValueError(f"No CSV files found in {me_path}")
#     num_me = len(me_files) if max_files is None else min(max_files, len(me_files))
#     print(f"Found {len(me_files)} male files. Loading first {num_me}...")
#     df_me_list = []
#     for i, f in enumerate(me_files[:num_me], 1):
#         try:
#             print(f"  Loading male file {i}/{num_me}: {os.path.basename(f)}")
#             df_temp = pd.read_csv(f, parse_dates=['Date'])
#             # Extract Elephant_ID from filename (e.g., "01me" from "01me_cold_dry_2009_08.csv")
#             filename = os.path.basename(f).replace('.csv', '')
#             elephant_id = filename.split('_')[0]
#             df_temp['Elephant_ID'] = elephant_id
#             df_me_list.append(df_temp)
#             print(f"    -> Loaded {len(df_temp)} rows for {elephant_id}")
#         except Exception as e:
#             print(f"    -> Skipped due to error: {e}")
#     df_me = pd.concat(df_me_list, ignore_index=True) if df_me_list else pd.DataFrame()
#     df_me['Sex'] = 'Male'
#     print(f"Total male rows: {len(df_me)}")
#     print(f"Unique male elephants: {sorted(df_me['Elephant_ID'].unique())}")
   
#     combined = pd.concat([df_fe, df_me], ignore_index=True)
#     print(f"Combined behavior data: {len(combined)} rows, {len(combined.columns)} columns")
#     print(f"Sample columns: {list(combined.columns[:5])}")  # First 5 cols for sanity check
#     return combined

# def merge_data(weather_df, behavior_df):
#     weather_df['Date'] = pd.to_datetime(weather_df['Date'])
#     behavior_df['Date'] = pd.to_datetime(behavior_df['Date'])
#     merged = pd.merge_asof(behavior_df.sort_values('Date'),
#                            weather_df.sort_values('Date'),
#                            on='Date', direction='nearest')
#     return merged

# # Function to calculate daily features from trajectory data
# def calculate_daily_features(df):
#     df['date'] = df['Date'].dt.date
#     features = []
   
#     for date, group in df.groupby('date'):
#         if len(group) < 2:
#             continue
       
#         # Total distance traveled (sum of step lengths in km)
#         total_dist = 0
#         for i in range(1, len(group)):
#             p1 = (group.iloc[i-1]['Latitude'], group.iloc[i-1]['Longitude'])
#             p2 = (group.iloc[i]['Latitude'], group.iloc[i]['Longitude'])
#             total_dist += geodesic(p1, p2).km
       
#         # Net displacement (straight-line distance from start to end of day in km)
#         p_start = (group.iloc[0]['Latitude'], group.iloc[0]['Longitude'])
#         p_end = (group.iloc[-1]['Latitude'], group.iloc[-1]['Longitude'])
#         displacement = geodesic(p_start, p_end).km
       
#         # Standard deviation of latitude and longitude (measure of area covered)
#         std_lat = group['Latitude'].std()
#         std_lon = group['Longitude'].std()
       
#         features.append({
#             'date': date,
#             'total_distance': total_dist,
#             'displacement': displacement,
#             'std_lat': std_lat,
#             'std_lon': std_lon
#         })
   
#     feature_df = pd.DataFrame(features)
#     feature_df['date'] = pd.to_datetime(feature_df['date'])
#     feature_df.sort_values('date', inplace=True)
#     return feature_df

# # Function to perform change point detection and identify behavior change periods
# def cluster_and_detect_changes(features, max_changes=20, min_segment_size=30):
#     cols = ['total_distance', 'displacement', 'std_lat', 'std_lon']
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(features[cols])
   
#     n = len(features)
   
#     def segment_cost(start, end):
#         if end - start < 2:
#             return 0
#         cost = 0
#         for i in range(X_scaled.shape[1]):
#             seg = X_scaled[start:end, i]
#             cost += np.sum((seg - np.mean(seg)) ** 2)
#         return cost
   
#     def find_best_split(start, end):
#         min_cost = np.inf
#         best_k = -1
#         for k in range(start + min_segment_size, end - min_segment_size + 1):
#             split_cost = segment_cost(start, k) + segment_cost(k, end)
#             if split_cost < min_cost:
#                 min_cost = split_cost
#                 best_k = k
#         return best_k, min_cost
   
#     current_segments = [(0, n)]
#     change_points = []
   
#     for _ in range(max_changes):
#         best_reduction = -np.inf
#         best_seg_idx = -1
#         best_k = -1
#         for idx, (start, end) in enumerate(current_segments):
#             orig_cost = segment_cost(start, end)
#             k, split_cost = find_best_split(start, end)
#             if k != -1:
#                 reduction = orig_cost - split_cost
#                 if reduction > best_reduction:
#                     best_reduction = reduction
#                     best_seg_idx = idx
#                     best_k = k
#         if best_seg_idx == -1 or best_reduction <= 0:
#             print(f"    Stopped after {_} changes: reduction={best_reduction:.2f}")
#             break
#         # Split the segment
#         start, end = current_segments.pop(best_seg_idx)
#         current_segments.insert(best_seg_idx, (best_k, end))
#         current_segments.insert(best_seg_idx, (start, best_k))
#         change_points.append(best_k)
   
#     change_points = sorted(set(change_points))
   
#     # Assign cluster labels to segments
#     labels = np.zeros(n, dtype=int)
#     cp = [0] + change_points + [n]
#     for i in range(len(cp) - 1):
#         labels[cp[i]:cp[i+1]] = i
   
#     features['cluster'] = labels
   
#     # Identify consecutive periods
#     periods = []
#     for key, group in groupby(features.iterrows(), key=lambda row: row[1]['cluster']):
#         group_list = list(group)
#         start_date = group_list[0][1]['date']
#         end_date = group_list[-1][1]['date']
#         periods.append({
#             'cluster': key,
#             'start': start_date,
#             'end': end_date
#         })
   
#     periods_df = pd.DataFrame(periods)
   
#     # Plot the total_distance over time colored by cluster to visualize changes
#     plt.figure(figsize=(12, 6))
#     plt.scatter(features['date'], features['total_distance'], c=features['cluster'], cmap='viridis')
#     plt.xlabel('Date')
#     plt.ylabel('Total Daily Distance (km)')
#     plt.title('Daily Movement Patterns with Detected Change Points')
#     plt.colorbar(label='Segment (Cluster)')
#     return features, periods_df

# def plot_single_group(group, elephant_id, year, base_dir):
#     """
#     Plots a single line chart: Latitude vs Date, colored by cluster (segment) for one elephant-year.
#     Saves as PNG.
#     """
#     if len(group) == 0:
#         print(f"  No data to plot for {elephant_id}_{year}")
#         return
   
#     # Sort by Date for time series
#     group = group.sort_values('Date')
   
#     # Plot: Line chart of Latitude over Date, colored by cluster
#     plt.figure(figsize=(12, 6))
#     unique_clusters = sorted(group['cluster'].unique())
#     colors = cm.tab10(np.linspace(0, 1, len(unique_clusters)))  # Auto colors
   
#     for i, cluster in enumerate(unique_clusters):
#         cluster_data = group[group['cluster'] == cluster]
#         plt.plot(cluster_data['Date'], cluster_data['Latitude'],
#                  color=colors[i], label=f'Segment {cluster}',
#                  linewidth=1.5, alpha=0.7)
   
#     plt.xlabel('Date')
#     plt.ylabel('Latitude')
#     plt.title(f'{elephant_id} - Year {year}: Latitude over Time by Segment (Custom CPD)')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
   
#     # Save plot
#     plot_path = os.path.join(base_dir, f"plot_segment_{elephant_id}_{year}.png")
#     plt.savefig(plot_path, dpi=300, bbox_inches='tight')
#     plt.close()  # Close figure to free memory
#     print(f"    Plot saved to: {plot_path}")

# def plot_clusters(csv_pattern, title="Elephant Trajectories by Segment"):
#     """
#     Loads all segmented_*.csv files matching the pattern,
#     combines data, and plots a single line chart: Latitude vs Date, colored by Segment.
#     """
#     base_dir = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/Clustering3"
#     csv_files = glob.glob(os.path.join(base_dir, csv_pattern))
#     if not csv_files:
#         print(f"No files found matching {csv_pattern}")
#         return
   
#     print(f"Loading {len(csv_files)} files for plotting...")
#     df_list = []
#     for f in csv_files:
#         df_temp = pd.read_csv(f, parse_dates=['Date'])
#         df_list.append(df_temp)
#     combined_df = pd.concat(df_list, ignore_index=True)
   
#     # Sort by Date for time series
#     combined_df = combined_df.sort_values('Date')
   
#     # Plot: Line chart of Latitude over Date, colored by Segment
#     plt.figure(figsize=(15, 8))
#     unique_segments = sorted(combined_df['cluster'].unique())
#     colors = plt.cm.tab10(np.linspace(0, 1, len(unique_segments)))  # Auto colors
   
#     for i, segment in enumerate(unique_segments):
#         segment_data = combined_df[combined_df['cluster'] == segment]
#         plt.plot(segment_data['Date'], segment_data['Latitude'],
#                  color=colors[i], label=f'Segment {segment}',
#                  linewidth=1.5, alpha=0.7)
   
#     plt.xlabel('Date')
#     plt.ylabel('Latitude')
#     plt.title(title)
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
   
#     # Save plot
#     plot_path = os.path.join(base_dir, "combined_segments_line_chart.png")
#     plt.savefig(plot_path, dpi=300, bbox_inches='tight')
#     print(f"Combined plot saved to: {plot_path}")
   
#     # For terminal: Save and print message; comment plt.show() if issues
#     # plt.show()  # Uncomment if you want interactive plot (e.g., in IDE)

# def main():
#     print("Starting main...")  # Confirm launch
   
#     halali_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/halali_weather_all_years.csv"
#     okaukuejo_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/okaukuejo_weather_all_years.csv"
#     fe_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/fe"
#     me_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/me"
#     base_out_dir = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/Clustering3"
   
#     print("Loading weather data...")
#     weather_df = load_weather_data(halali_path, okaukuejo_path)
#     print(f"Weather loaded: {len(weather_df)} rows")
   
#     print("Loading behavior data (full load: no file limit)...")
#     behavior_df = load_behavior_data(fe_path, me_path, max_files=None)  # Load all files
   
#     print("Merging data...")
#     merged_df = merge_data(weather_df, behavior_df)
#     print(f"Merged: {len(merged_df)} rows")
   
#     # Updated features list to include all specified parameters (though not directly used in CPD now)
#     features = [
#         'Longitude', 'Latitude', 'Time', 'DateTime', 'Sex', 'Year', 
#         'Temp_C', 'Temp_F', 'Dew_C', 'Dew_F', 'Humidity_%', 
#         'Wind_Kph', 'Wind_Mph', 'Press_Hg', 'Press_Mb', 
#         'Precip_mm', 'Precip_in'
#     ]
#     # Filter to those available in the merged data
#     features = [f for f in features if f in merged_df.columns]
#     print(f"Available features: {features}")
   
#     # Extract Year from Date if not present
#     if 'Year' not in merged_df.columns:
#         merged_df['Year'] = merged_df['Date'].dt.year
   
#     # Segment separately for each Elephant_ID and Year using custom variance-based CPD
#     print("Segmenting separately for each elephant and year (custom variance-based CPD only)...")
#     groups = merged_df.groupby(['Elephant_ID', 'Year'])
#     print(f"Total groups to process: {len(groups)}")
#     for i, ((elephant_id, year), group) in enumerate(groups, 1):
#         if len(group) < 10:  # Skip very small groups
#             print(f"  [{i}/{len(groups)}] Skipping {elephant_id}_{year}: too few rows ({len(group)})")
#             continue
       
#         print(f"  [{i}/{len(groups)}] Processing {elephant_id}_{year} ({len(group)} rows)...")
       
#         # Calculate daily features for this group
#         daily_features = calculate_daily_features(group)
#         print(f"    Computed daily features for {len(daily_features)} days")
       
#         # Apply custom change-point detection (tune params here)
#         print("    Detecting change points...")
#         clustered_features, change_periods = cluster_and_detect_changes(daily_features, max_changes=12, min_segment_size=25)  # Tuned example
#         print(f"    Detected {len(change_periods)} segments")
       
#         # Merge cluster (segment) back to the original group data
#         group['date'] = group['Date'].dt.date
#         group['date'] = pd.to_datetime(group['date'])
#         group = group.merge(clustered_features[['date', 'cluster']], on='date', how='left').fillna({'cluster': -1})
       
#         # Select only desired columns for output CSV: essential + specified weather vars
#         desired_cols = [
#             'Date', 'Latitude', 'Longitude', 'Elephant_ID', 'Year', 'cluster',  # Essentials for plotting/segments
#             'Temp_C', 'Temp_F', 'Humidity_%', 'Wind_Mph', 'Press_Hg', 'Precip_mm'  # Specified weather (skipped duplicates/irrelevant)
#         ]
#         # Filter to available columns
#         available_desired = [col for col in desired_cols if col in group.columns]
#         group_selected = group[available_desired]
       
#         # Save selected data to CSV
#         out_file = os.path.join(base_out_dir, f"segmented_data_{elephant_id}_{year}.csv")
#         os.makedirs(base_out_dir, exist_ok=True)
#         group_selected.to_csv(out_file, index=False)
#         print(f"    Saved selected columns to: {out_file}")
       
#         # Print detected periods
#         print(f"    Detected Behavior Periods for {elephant_id}_{year}:")
#         print(change_periods)
       
#         # Generate individual plot for this elephant-year, colored by cluster (segment)
#         print("    Generating individual plot...")
#         plot_single_group(group, elephant_id, year, base_out_dir)
   
#     print("All processing complete!")
   
#     # Optional: Generate combined plot for all (colored by Segment)
#     print("Generating combined plot...")
#     plot_clusters("segmented_data_*.csv", "All Elephants: Latitude over Time by Segment (Custom Variance-based CPD)")

# if __name__ == "__main__":
#     main()


# Required installs: pip install ruptures pandas scikit-learn matplotlib geopy
import pandas as pd
import numpy as np
import glob
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import SpectralClustering  # For spectral clustering
import matplotlib.pyplot as plt  # For plotting
import matplotlib.cm as cm  # For colormaps
from datetime import datetime
from geopy.distance import geodesic
from itertools import groupby

def load_weather_data(halali_path, okaukuejo_path):
    df_halali = pd.read_csv(halali_path)
    df_okau = pd.read_csv(okaukuejo_path)
    df_halali['Region'] = 'Halali'
    df_okau['Region'] = 'Okaukuejo'
    return pd.concat([df_halali, df_okau], ignore_index=True)

def load_behavior_data(fe_path, me_path, max_files=None):  # Default to None (load all)
    print(f"Loading behavior data from {fe_path} and {me_path} (max {max_files} files per sex)...")
   
    # Load females
    fe_files = glob.glob(os.path.join(fe_path, "*.csv"))
    if not fe_files:
        raise ValueError(f"No CSV files found in {fe_path}")
    num_fe = len(fe_files) if max_files is None else min(max_files, len(fe_files))
    print(f"Found {len(fe_files)} female files. Loading first {num_fe}...")
    df_fe_list = []
    for i, f in enumerate(fe_files[:num_fe], 1):
        try:
            print(f"  Loading female file {i}/{num_fe}: {os.path.basename(f)}")
            df_temp = pd.read_csv(f, parse_dates=['Date'])
            # Extract Elephant_ID from filename (e.g., "01fe" from "01fe_cold_dry_2009_08.csv")
            filename = os.path.basename(f).replace('.csv', '')
            elephant_id = filename.split('_')[0]
            df_temp['Elephant_ID'] = elephant_id
            df_fe_list.append(df_temp)
            print(f"    -> Loaded {len(df_temp)} rows for {elephant_id}")
        except Exception as e:
            print(f"    -> Skipped due to error: {e}")
    df_fe = pd.concat(df_fe_list, ignore_index=True) if df_fe_list else pd.DataFrame()
    df_fe['Sex'] = 'Female'
    print(f"Total female rows: {len(df_fe)}")
    print(f"Unique female elephants: {sorted(df_fe['Elephant_ID'].unique())}")
   
    # Load males
    me_files = glob.glob(os.path.join(me_path, "*.csv"))
    if not me_files:
        raise ValueError(f"No CSV files found in {me_path}")
    num_me = len(me_files) if max_files is None else min(max_files, len(me_files))
    print(f"Found {len(me_files)} male files. Loading first {num_me}...")
    df_me_list = []
    for i, f in enumerate(me_files[:num_me], 1):
        try:
            print(f"  Loading male file {i}/{num_me}: {os.path.basename(f)}")
            df_temp = pd.read_csv(f, parse_dates=['Date'])
            # Extract Elephant_ID from filename (e.g., "01me" from "01me_cold_dry_2009_08.csv")
            filename = os.path.basename(f).replace('.csv', '')
            elephant_id = filename.split('_')[0]
            df_temp['Elephant_ID'] = elephant_id
            df_me_list.append(df_temp)
            print(f"    -> Loaded {len(df_temp)} rows for {elephant_id}")
        except Exception as e:
            print(f"    -> Skipped due to error: {e}")
    df_me = pd.concat(df_me_list, ignore_index=True) if df_me_list else pd.DataFrame()
    df_me['Sex'] = 'Male'
    print(f"Total male rows: {len(df_me)}")
    print(f"Unique male elephants: {sorted(df_me['Elephant_ID'].unique())}")
   
    combined = pd.concat([df_fe, df_me], ignore_index=True)
    print(f"Combined behavior data: {len(combined)} rows, {len(combined.columns)} columns")
    print(f"Sample columns: {list(combined.columns[:5])}")  # First 5 cols for sanity check
    return combined

def merge_data(weather_df, behavior_df):
    weather_df['Date'] = pd.to_datetime(weather_df['Date'])
    behavior_df['Date'] = pd.to_datetime(behavior_df['Date'])
    merged = pd.merge_asof(behavior_df.sort_values('Date'),
                           weather_df.sort_values('Date'),
                           on='Date', direction='nearest')
    return merged

# Function to calculate daily features from trajectory data
def calculate_daily_features(df):
    df['date'] = df['Date'].dt.date
    features = []
   
    for date, group in df.groupby('date'):
        if len(group) < 2:
            continue
       
        # Total distance traveled (sum of step lengths in km)
        total_dist = 0
        for i in range(1, len(group)):
            p1 = (group.iloc[i-1]['Latitude'], group.iloc[i-1]['Longitude'])
            p2 = (group.iloc[i]['Latitude'], group.iloc[i]['Longitude'])
            total_dist += geodesic(p1, p2).km
       
        # Net displacement (straight-line distance from start to end of day in km)
        p_start = (group.iloc[0]['Latitude'], group.iloc[0]['Longitude'])
        p_end = (group.iloc[-1]['Latitude'], group.iloc[-1]['Longitude'])
        displacement = geodesic(p_start, p_end).km
       
        # Standard deviation of latitude and longitude (measure of area covered)
        std_lat = group['Latitude'].std()
        std_lon = group['Longitude'].std()
       
        features.append({
            'date': date,
            'total_distance': total_dist,
            'displacement': displacement,
            'std_lat': std_lat,
            'std_lon': std_lon
        })
   
    feature_df = pd.DataFrame(features)
    feature_df['date'] = pd.to_datetime(feature_df['date'])
    feature_df.sort_values('date', inplace=True)
    return feature_df

# Function to perform change point detection and identify behavior change periods
def cluster_and_detect_changes(features, max_changes=20, min_segment_size=15):
    cols = ['total_distance', 'displacement', 'std_lat', 'std_lon']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features[cols])
   
    n = len(features)
   
    def segment_cost(start, end):
        if end - start < 2:
            return 0
        cost = 0
        for i in range(X_scaled.shape[1]):
            seg = X_scaled[start:end, i]
            cost += np.sum((seg - np.mean(seg)) ** 2)
        return cost
   
    def find_best_split(start, end):
        min_cost = np.inf
        best_k = -1
        for k in range(start + min_segment_size, end - min_segment_size + 1):
            split_cost = segment_cost(start, k) + segment_cost(k, end)
            if split_cost < min_cost:
                min_cost = split_cost
                best_k = k
        return best_k, min_cost
   
    current_segments = [(0, n)]
    change_points = []
   
    for _ in range(max_changes):
        best_reduction = -np.inf
        best_seg_idx = -1
        best_k = -1
        for idx, (start, end) in enumerate(current_segments):
            orig_cost = segment_cost(start, end)
            k, split_cost = find_best_split(start, end)
            if k != -1:
                reduction = orig_cost - split_cost
                if reduction > best_reduction:
                    best_reduction = reduction
                    best_seg_idx = idx
                    best_k = k
        if best_seg_idx == -1 or best_reduction <= 0:
            print(f"    Stopped after {_} changes: reduction={best_reduction:.2f}")
            break
        # Split the segment
        start, end = current_segments.pop(best_seg_idx)
        current_segments.insert(best_seg_idx, (best_k, end))
        current_segments.insert(best_seg_idx, (start, best_k))
        change_points.append(best_k)
   
    change_points = sorted(set(change_points))
   
    # Assign segment labels to days (from CPD)
    labels = np.zeros(n, dtype=int)
    cp = [0] + change_points + [n]
    for i in range(len(cp) - 1):
        labels[cp[i]:cp[i+1]] = i
   
    features['segment'] = labels  # Rename to 'segment' for clarity
   
    # Identify consecutive periods
    periods = []
    for key, group in groupby(features.iterrows(), key=lambda row: row[1]['segment']):
        group_list = list(group)
        start_date = group_list[0][1]['date']
        end_date = group_list[-1][1]['date']
        periods.append({
            'segment': key,
            'start': start_date,
            'end': end_date
        })
   
    periods_df = pd.DataFrame(periods)
   
    # Plot the total_distance over time colored by segment to visualize changes
    plt.figure(figsize=(12, 6))
    plt.scatter(features['date'], features['total_distance'], c=features['segment'], cmap='viridis')
    plt.xlabel('Date')
    plt.ylabel('Total Daily Distance (km)')
    plt.title('Daily Movement Patterns with Detected Change Points')
    plt.colorbar(label='Segment')
    plt.close()  # Close plot as it's internal
    return features, periods_df

# Function to apply spectral clustering to segment means
# Function to apply spectral clustering to segment means
def apply_spectral_clustering(features, n_clusters=4):
    """
    Applies spectral clustering to the mean features of each segment.
    Groups similar segments into final clusters.
    Handles cases with <2 segments gracefully.
    """
    # Compute mean features per segment
    segment_cols = ['total_distance', 'displacement', 'std_lat', 'std_lon']
    segment_stats = features.groupby('segment')[segment_cols].mean()
    
    if len(segment_stats) < n_clusters:
        print(f"Warning: Only {len(segment_stats)} segment(s) - assigning all to cluster 0 (no clustering possible)")
        segment_stats['spectral_cluster'] = 0  # Dummy single cluster
        features['spectral_cluster'] = 0
        return features
    
    if len(segment_stats) < n_clusters:
        print(f"Warning: Only {len(segment_stats)} segments, adjusting n_clusters to {len(segment_stats)}")
        n_clusters = len(segment_stats)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(segment_stats)
    
    # Spectral clustering with RBF affinity
    spectral = SpectralClustering(n_clusters=n_clusters, affinity='rbf', random_state=42)
    segment_stats['spectral_cluster'] = spectral.fit_predict(X_scaled)
    
    # Map spectral_cluster back to features
    features = features.merge(segment_stats['spectral_cluster'], left_on='segment', right_index=True, how='left')
    
    return features

def plot_single_group(group, elephant_id, year, base_dir):
    """
    Plots a single line chart: Latitude vs Date, colored by spectral_cluster for one elephant-year.
    Saves as PNG.
    """
    if len(group) == 0:
        print(f"  No data to plot for {elephant_id}_{year}")
        return
   
    # Sort by Date for time series
    group = group.sort_values('Date')
   
    # Plot: Line chart of Latitude over Date, colored by spectral_cluster
    plt.figure(figsize=(12, 6))
    unique_clusters = sorted(group['spectral_cluster'].unique())
    colors = cm.tab10(np.linspace(0, 1, len(unique_clusters)))  # Auto colors
   
    for i, cluster in enumerate(unique_clusters):
        cluster_data = group[group['spectral_cluster'] == cluster]
        plt.plot(cluster_data['Date'], cluster_data['Latitude'],
                 color=colors[i], label=f'Spectral Cluster {cluster}',
                 linewidth=1.5, alpha=0.7)
   
    plt.xlabel('Date')
    plt.ylabel('Latitude')
    plt.title(f'{elephant_id} - Year {year}: Latitude over Time by Spectral Cluster (Post-CPD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
   
    # Save plot
    plot_path = os.path.join(base_dir, f"plot_spectral_{elephant_id}_{year}.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    print(f"    Plot saved to: {plot_path}")

def plot_clusters(csv_pattern, title="Elephant Trajectories by Spectral Cluster"):
    """
    Loads all segmented_*.csv files matching the pattern,
    combines data, and plots a single line chart: Latitude vs Date, colored by Spectral Cluster.
    """
    base_dir = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/Clustering4"
    csv_files = glob.glob(os.path.join(base_dir, csv_pattern))
    if not csv_files:
        print(f"No files found matching {csv_pattern}")
        return
   
    print(f"Loading {len(csv_files)} files for plotting...")
    df_list = []
    for f in csv_files:
        df_temp = pd.read_csv(f, parse_dates=['Date'])
        df_list.append(df_temp)
    combined_df = pd.concat(df_list, ignore_index=True)
   
    # Sort by Date for time series
    combined_df = combined_df.sort_values('Date')
   
    # Plot: Line chart of Latitude over Date, colored by Spectral Cluster
    plt.figure(figsize=(15, 8))
    unique_clusters = sorted(combined_df['spectral_cluster'].unique())
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_clusters)))  # Auto colors
   
    for i, cluster in enumerate(unique_clusters):
        cluster_data = combined_df[combined_df['spectral_cluster'] == cluster]
        plt.plot(cluster_data['Date'], cluster_data['Latitude'],
                 color=colors[i], label=f'Spectral Cluster {cluster}',
                 linewidth=1.5, alpha=0.7)
   
    plt.xlabel('Date')
    plt.ylabel('Latitude')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
   
    # Save plot
    plot_path = os.path.join(base_dir, "combined_spectral_clusters_line_chart.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Combined plot saved to: {plot_path}")
   
    # For terminal: Save and print message; comment plt.show() if issues
    # plt.show()  # Uncomment if you want interactive plot (e.g., in IDE)

def main():
    print("Starting main...")  # Confirm launch
   
    halali_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/halali_weather_all_years.csv"
    okaukuejo_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/okaukuejo_weather_all_years.csv"
    fe_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/fe"
    me_path = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/data/me"
    base_out_dir = r"G:/Work (UoP)/MARC/ABM/Animal/ai4covid_clustering-dev - Elephants - Pure Markov/Clustering4"
   
    print("Loading weather data...")
    weather_df = load_weather_data(halali_path, okaukuejo_path)
    print(f"Weather loaded: {len(weather_df)} rows")
   
    print("Loading behavior data (full load: no file limit)...")
    behavior_df = load_behavior_data(fe_path, me_path, max_files=None)  # Load all files
   
    print("Merging data...")
    merged_df = merge_data(weather_df, behavior_df)
    print(f"Merged: {len(merged_df)} rows")
   
    # Updated features list to include all specified parameters (though not directly used in CPD now)
    features = [
        'Longitude', 'Latitude', 'Time', 'DateTime', 'Sex', 'Year', 
        'Temp_C', 'Temp_F', 'Dew_C', 'Dew_F', 'Humidity_%', 
        'Wind_Kph', 'Wind_Mph', 'Press_Hg', 'Press_Mb', 
        'Precip_mm', 'Precip_in'
    ]
    # Filter to those available in the merged data
    features = [f for f in features if f in merged_df.columns]
    print(f"Available features: {features}")
   
    # Extract Year from Date if not present
    if 'Year' not in merged_df.columns:
        merged_df['Year'] = merged_df['Date'].dt.year
   
    # Segment separately for each Elephant_ID and Year using custom variance-based CPD + Spectral Clustering
    print("Processing separately for each elephant and year (CPD + Spectral Clustering)...")
    groups = merged_df.groupby(['Elephant_ID', 'Year'])
    print(f"Total groups to process: {len(groups)}")
    for i, ((elephant_id, year), group) in enumerate(groups, 1):
        if len(group) < 10:  # Skip very small groups
            print(f"  [{i}/{len(groups)}] Skipping {elephant_id}_{year}: too few rows ({len(group)})")
            continue
       
        print(f"  [{i}/{len(groups)}] Processing {elephant_id}_{year} ({len(group)} rows)...")

        # Calculate daily features for this group
        daily_features = calculate_daily_features(group)
        print(f"    Computed daily features for {len(daily_features)} days")

        # Step 1: Variance-based CPD to get segments (tuned for more)
        print("    Detecting change points...")
        segmented_features, change_periods = cluster_and_detect_changes(daily_features, max_changes=20, min_segment_size=15)
        print(f"    Detected {len(change_periods)} segments from CPD")

        # Debug: Print num segments
        num_segments = len(segmented_features['segment'].unique())
        print(f"    Num segments from CPD: {num_segments}")

        # Step 2: Spectral clustering on segment means (tuned to 4)
        print("    Applying spectral clustering to segments...")
        clustered_features = apply_spectral_clustering(segmented_features, n_clusters=4)
        print(f"    Spectral clustering produced {clustered_features['spectral_cluster'].nunique()} clusters")
       
        # Merge spectral_cluster back to the original group data
        group['date'] = group['Date'].dt.date
        group['date'] = pd.to_datetime(group['date'])
        group = group.merge(clustered_features[['date', 'spectral_cluster']], on='date', how='left').fillna({'spectral_cluster': -1})
       
        # Select only desired columns for output CSV: essential + specified weather vars
        desired_cols = [
            'Date', 'Latitude', 'Longitude', 'Elephant_ID', 'Year', 'spectral_cluster',  # Essentials + final cluster
            'Temp_C', 'Temp_F', 'Humidity_%', 'Wind_Mph', 'Press_Hg', 'Precip_mm'  # Specified weather
        ]
        # Filter to available columns
        available_desired = [col for col in desired_cols if col in group.columns]
        group_selected = group[available_desired]
       
        # Save selected data to CSV
        out_file = os.path.join(base_out_dir, f"segmented_spectral_{elephant_id}_{year}.csv")
        os.makedirs(base_out_dir, exist_ok=True)
        group_selected.to_csv(out_file, index=False)
        print(f"    Saved selected columns to: {out_file}")
       
        # Print detected periods (from CPD segments)
        print(f"    Detected Behavior Periods (CPD Segments) for {elephant_id}_{year}:")
        print(change_periods)
       
        # Generate individual plot for this elephant-year, colored by spectral_cluster
        print("    Generating individual plot...")
        plot_single_group(group, elephant_id, year, base_out_dir)
   
    print("All processing complete!")
   
    # Optional: Generate combined plot for all (colored by Spectral Cluster)
    print("Generating combined plot...")
    plot_clusters("segmented_spectral_*.csv", "All Elephants: Latitude over Time by Spectral Cluster (Post-CPD)")

if __name__ == "__main__":
    main()