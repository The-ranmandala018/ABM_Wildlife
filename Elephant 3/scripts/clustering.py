# import pandas as pd
# import os
# import numpy as np
# from geopy.distance import geodesic
# from sklearn.preprocessing import StandardScaler
# from itertools import groupby
# import matplotlib.pyplot as plt
# import folium  # You may need to install this: pip install folium

# # Define relative paths (assuming script is run from the project root: ai4covid_clustering-dev)
# dir_fe = '../data/fe'
# dir_me = '../data/me'  # Assuming this is the correct path for males; adjust if needed

# # Output directory
# output_dir = 'clustering_data'

# # Function to get all elephant IDs for a gender
# def get_all_elephant_ids(gender='fe'):
#     if gender == 'fe':
#         data_dir = dir_fe
#     elif gender == 'me':
#         data_dir = dir_me
#     else:
#         raise ValueError("Gender must be 'fe' or 'me'")
    
#     files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
#     ids = set(f.split('_')[0] for f in files if '_' in f)
#     return sorted(ids)

# # Function to load all data for a specific elephant
# def load_elephant_data(elephant_id, gender='fe'):
#     if gender == 'fe':
#         data_dir = dir_fe
#     elif gender == 'me':
#         data_dir = dir_me
#     else:
#         raise ValueError("Gender must be 'fe' or 'me'")
    
#     files = [f for f in os.listdir(data_dir) if f.startswith(elephant_id) and f.endswith('.csv')]
#     if not files:
#         raise ValueError(f"No files found for {elephant_id} in {data_dir}")
    
#     dfs = []
#     for file in files:
#         file_path = os.path.join(data_dir, file)
#         df = pd.read_csv(file_path)
#         dfs.append(df)
    
#     all_df = pd.concat(dfs, ignore_index=True)
#     all_df['DateTime'] = pd.to_datetime(all_df['DateTime'])
#     all_df.sort_values('DateTime', inplace=True)
#     return all_df

# # Function to calculate daily features from trajectory data
# def calculate_daily_features(df):
#     df['date'] = df['DateTime'].dt.date
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

# # Function to create HTML map with points colored by cluster
# def create_behavior_map(df, map_name, cluster_color_map, subdir):
#     # Subset has clusters covered by the map
#     m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)
    
#     for _, row in df.iterrows():
#         cluster = row['cluster']
#         color = cluster_color_map.get(cluster, 'black')  # Default to black if not in map
#         folium.CircleMarker(
#             location=[row['Latitude'], row['Longitude']],
#             radius=2,
#             color=color,
#             fill=True,
#             fill_color=color,
#             fill_opacity=0.6,
#             popup=f"Cluster: {cluster}<br>DateTime: {row['DateTime']}"
#         ).add_to(m)
    
#     map_file = f'{map_name}_behavior_map.html'
#     full_path = os.path.join(subdir, map_file)
#     m.save(full_path)
#     print(f"HTML map saved to {full_path}")

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

# # Main processing loop for all elephants
# if __name__ == "__main__":
#     for gender in ['fe', 'me']:
#         subdir = os.path.join(output_dir, gender)
#         os.makedirs(subdir, exist_ok=True)
        
#         elephant_ids = get_all_elephant_ids(gender)
#         for elephant_id in elephant_ids:
#             try:
#                 # Load data
#                 df = load_elephant_data(elephant_id, gender)
#                 print(f"Loaded {len(df)} records for {elephant_id}")
                
#                 # Calculate features
#                 daily_features = calculate_daily_features(df)
#                 print(f"Computed features for {len(daily_features)} days")
                
#                 # Cluster and detect changes (adjust max_changes and min_segment_size as needed for your data)
#                 clustered_features, change_periods = cluster_and_detect_changes(daily_features, max_changes=20, min_segment_size=30)
                
#                 # Save cluster plot
#                 plot_file = f'{elephant_id}_cluster_plot.png'
#                 plot_path = os.path.join(subdir, plot_file)
#                 plt.savefig(plot_path)
#                 plt.close()
#                 print(f"Cluster plot saved to {plot_path}")
                
#                 # Assign clusters back to original df for mapping
#                 df['date'] = df['DateTime'].dt.date
#                 df['date'] = pd.to_datetime(df['date'])  # Convert to datetime64 to match clustered_features
#                 df = df.merge(clustered_features[['date', 'cluster']], on='date', how='left').fillna({'cluster': -1})  # Unclustered as noise
                
#                 # Add year for grouping
#                 df['year'] = df['DateTime'].dt.year
                
#                 # Create global color map for consistency across years
#                 unique_clusters = sorted(df['cluster'].unique())
#                 colors = ['gray', 'red', 'blue', 'green', 'purple', 'orange', 'yellow', 'pink', 'brown']  # 0 for noise, then others
#                 cluster_color_map = {cluster: colors[(i % (len(colors) - 1)) + 1] if cluster != -1 else 'gray' for i, cluster in enumerate(unique_clusters)}
                
#                 # Create maps per year
#                 for year in sorted(df['year'].unique()):
#                     df_year = df[df['year'] == year]
#                     if not df_year.empty:
#                         create_behavior_map(df_year, f"{elephant_id}_{year}", cluster_color_map, subdir)
                
#                 # Print detected behavior periods (potential season transitions)
#                 print(f"\nDetected Behavior Periods for {elephant_id} (Clusters):")
#                 print(change_periods)
                
#                 # Save results to CSV if needed
#                 features_file = f'{elephant_id}_clustered_features.csv'
#                 features_path = os.path.join(subdir, features_file)
#                 clustered_features.to_csv(features_path, index=False)
                
#                 periods_file = f'{elephant_id}_behavior_periods.csv'
#                 periods_path = os.path.join(subdir, periods_file)
#                 change_periods.to_csv(periods_path, index=False)
                
#                 print(f"CSV files saved to {features_path} and {periods_path}")
            
#             except Exception as e:
#                 print(f"Error processing {elephant_id} ({gender}): {e}")





import pandas as pd
import os
import numpy as np
from geopy.distance import geodesic
from sklearn.preprocessing import StandardScaler
from itertools import groupby
import matplotlib.pyplot as plt
import folium  # You may need to install this: pip install folium

# Define relative paths (assuming script is run from the project root: ai4covid_clustering-dev)
dir_fe = '../data/fe'
dir_me = '../data/me'  # Assuming this is the correct path for males; adjust if needed

# Output directory
output_dir = 'clustering_data'

# Function to get all elephant IDs for a gender
def get_all_elephant_ids(gender='fe'):
    if gender == 'fe':
        data_dir = dir_fe
    elif gender == 'me':
        data_dir = dir_me
    else:
        raise ValueError("Gender must be 'fe' or 'me'")
    
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    ids = set(f.split('_')[0] for f in files if '_' in f)
    return sorted(ids)

# Function to load all data for a specific elephant
def load_elephant_data(elephant_id, gender='fe'):
    if gender == 'fe':
        data_dir = dir_fe
    elif gender == 'me':
        data_dir = dir_me
    else:
        raise ValueError("Gender must be 'fe' or 'me'")
    
    files = [f for f in os.listdir(data_dir) if f.startswith(elephant_id) and f.endswith('.csv')]
    if not files:
        raise ValueError(f"No files found for {elephant_id} in {data_dir}")
    
    dfs = []
    for file in files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        dfs.append(df)
    
    all_df = pd.concat(dfs, ignore_index=True)
    all_df['DateTime'] = pd.to_datetime(all_df['DateTime'])
    all_df.sort_values('DateTime', inplace=True)
    return all_df

# Function to calculate daily features from trajectory data
def calculate_daily_features(df):
    df['date'] = df['DateTime'].dt.date
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

# Function to create HTML map with points colored by cluster
def create_behavior_map(df, map_name, cluster_color_map, subdir):
    # Subset has clusters covered by the map
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)
    
    for _, row in df.iterrows():
        cluster = row['cluster']
        color = cluster_color_map.get(cluster, 'black')  # Default to black if not in map
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=2,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=f"Cluster: {cluster}<br>DateTime: {row['DateTime']}<br>Cluster Start: {row['cluster_start']}<br>Cluster End: {row['cluster_end']}"
        ).add_to(m)
    
    map_file = f'{map_name}_behavior_map.html'
    full_path = os.path.join(subdir, map_file)
    m.save(full_path)
    print(f"HTML map saved to {full_path}")

# Function to perform change point detection and identify behavior change periods
def cluster_and_detect_changes(features, max_changes=20, min_segment_size=30):
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
            break
        # Split the segment
        start, end = current_segments.pop(best_seg_idx)
        current_segments.insert(best_seg_idx, (best_k, end))
        current_segments.insert(best_seg_idx, (start, best_k))
        change_points.append(best_k)
    
    change_points = sorted(set(change_points))
    
    # Assign cluster labels to segments
    labels = np.zeros(n, dtype=int)
    cp = [0] + change_points + [n]
    for i in range(len(cp) - 1):
        labels[cp[i]:cp[i+1]] = i
    
    features['cluster'] = labels
    
    # Identify consecutive periods
    periods = []
    for key, group in groupby(features.iterrows(), key=lambda row: row[1]['cluster']):
        group_list = list(group)
        start_date = group_list[0][1]['date']
        end_date = group_list[-1][1]['date']
        periods.append({
            'cluster': key,
            'start': start_date,
            'end': end_date
        })
    
    periods_df = pd.DataFrame(periods)
    
    # Plot the total_distance over time colored by cluster to visualize changes
    plt.figure(figsize=(12, 6))
    plt.scatter(features['date'], features['total_distance'], c=features['cluster'], cmap='viridis')
    plt.xlabel('Date')
    plt.ylabel('Total Daily Distance (km)')
    plt.title('Daily Movement Patterns with Detected Change Points')
    plt.colorbar(label='Segment (Cluster)')
    return features, periods_df

# Main processing loop for all elephants
if __name__ == "__main__":
    for gender in ['fe', 'me']:
        subdir = os.path.join(output_dir, gender)
        os.makedirs(subdir, exist_ok=True)
        
        elephant_ids = get_all_elephant_ids(gender)
        for elephant_id in elephant_ids:
            try:
                # Load data
                df = load_elephant_data(elephant_id, gender)
                print(f"Loaded {len(df)} records for {elephant_id}")
                
                # Calculate features
                daily_features = calculate_daily_features(df)
                print(f"Computed features for {len(daily_features)} days")
                
                # Cluster and detect changes (adjust max_changes and min_segment_size as needed for your data)
                clustered_features, change_periods = cluster_and_detect_changes(daily_features, max_changes=20, min_segment_size=30)
                
                # Save cluster plot
                plot_file = f'{elephant_id}_cluster_plot.png'
                plot_path = os.path.join(subdir, plot_file)
                plt.savefig(plot_path)
                plt.close()
                print(f"Cluster plot saved to {plot_path}")
                
                # Assign clusters back to original df for mapping
                df['date'] = df['DateTime'].dt.date
                df['date'] = pd.to_datetime(df['date'])  # Convert to datetime64 to match clustered_features
                df = df.merge(clustered_features[['date', 'cluster']], on='date', how='left').fillna({'cluster': -1})  # Unclustered as noise
                
                # Add cluster start and end
                cluster_dates = {row['cluster']: (row['start'], row['end']) for _, row in change_periods.iterrows()}
                df['cluster_start'] = df['cluster'].map(lambda c: cluster_dates.get(c, (pd.NaT, pd.NaT))[0])
                df['cluster_end'] = df['cluster'].map(lambda c: cluster_dates.get(c, (pd.NaT, pd.NaT))[1])
                
                # Add year for grouping
                df['year'] = df['DateTime'].dt.year
                
                # Create global color map for consistency across years
                unique_clusters = sorted(df['cluster'].unique())
                colors = ['gray', 'red', 'blue', 'green', 'purple', 'orange', 'yellow', 'pink', 'brown']  # 0 for noise, then others
                cluster_color_map = {cluster: colors[(i % (len(colors) - 1)) + 1] if cluster != -1 else 'gray' for i, cluster in enumerate(unique_clusters)}
                
                # Create maps per year
                for year in sorted(df['year'].unique()):
                    df_year = df[df['year'] == year]
                    if not df_year.empty:
                        create_behavior_map(df_year, f"{elephant_id}_{year}", cluster_color_map, subdir)
                
                # Print detected behavior periods (potential season transitions)
                print(f"\nDetected Behavior Periods for {elephant_id} (Clusters):")
                print(change_periods)
                
                # Save results to CSV if needed
                features_file = f'{elephant_id}_clustered_features.csv'
                features_path = os.path.join(subdir, features_file)
                clustered_features.to_csv(features_path, index=False)
                
                periods_file = f'{elephant_id}_behavior_periods.csv'
                periods_path = os.path.join(subdir, periods_file)
                change_periods.to_csv(periods_path, index=False)
                
                print(f"CSV files saved to {features_path} and {periods_path}")
            
            except Exception as e:
                print(f"Error processing {elephant_id} ({gender}): {e}")