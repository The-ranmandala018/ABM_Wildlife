


# import folium
# import pandas as pd
# import os

# # Input and output paths
# input_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\clusters\fe"
# output_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Home_Clusters"

# # Create output directory if it doesn't exist
# if not os.path.exists(output_path):
#     os.makedirs(output_path)

# # Iterate over each CSV file in the input path
# for file_name in os.listdir(input_path):
#     if file_name.endswith(".csv"):
#         print(f"Processing {file_name}")
#         file_path = os.path.join(input_path, file_name)
        
#         # Read the CSV
#         df = pd.read_csv(file_path)
        
#         # Filter rows between 3:00 AM and 4:00 AM (inclusive)
#         morning_df = df[df['Time'].between('00:00:00', '03:00:00')]
        
#         if not morning_df.empty:
#             # Compute mean latitude and longitude for map centering
#             mean_lat = morning_df['Latitude'].mean()
#             mean_lon = morning_df['Longitude'].mean()
            
#             # Create Folium map centered on mean location
#             m = folium.Map(location=[mean_lat, mean_lon], zoom_start=15, tiles="OpenStreetMap")
            
#             # Add markers for each point
#             for _, row in morning_df.iterrows():
#                 popup_text = f"Date: {row['Date']}<br>Time: {row['Time']}<br>Elephant ID: {row['individual-local-identifier']}"
#                 folium.CircleMarker(
#                     location=[row['Latitude'], row['Longitude']],
#                     radius=5,
#                     color='blue',
#                     fill=True,
#                     fill_color='blue',
#                     popup=popup_text
#                 ).add_to(m)
            
#             # Save the map as HTML
#             map_file = os.path.join(output_path, file_name.replace('.csv', '_morning_map.html'))
#             m.save(map_file)
#             print(f"Saved map: {map_file}")
#         else:
#             print(f"No data between 12:00 AM and 4:00 AM in {file_name}")

import folium
import pandas as pd
import numpy as np
import os

# Define color palette for clusters
cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
        '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff',
        '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
        '#000075', '#808080'] * 100

# Input and output paths
input_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\clusters\fe"
output_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Home_Clusters"

# Create output directory if it doesn't exist
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Iterate over each CSV file in the input path
for file_name in os.listdir(input_path):
    if file_name.endswith(".csv"):
        print(f"Processing {file_name}")
        file_path = os.path.join(input_path, file_name)
        
        # Read the CSV
        df = pd.read_csv(file_path)
        
        # Get the cluster column name (assuming it exists as in the original clustering code)
        cluster_column = [column for column in df.columns if column.startswith("Cluster_DBSCAN")][0]
        
        # Filter rows between 00:00:00 and 03:00:00 (inclusive)
        morning_df = df[df['Time'].between('00:00:00', '04:00:00')]
        
        if not morning_df.empty:
            # Compute mean latitude and longitude for map centering
            mean_lat = morning_df['Latitude'].mean()
            mean_lon = morning_df['Longitude'].mean()
            
            # Create Folium map centered on mean location
            m = folium.Map(location=[mean_lat, mean_lon], zoom_start=15, tiles="OpenStreetMap")
            
            # Get unique clusters in morning data
            unique_clusters = morning_df[cluster_column].unique()
            
            # Plot individual GPS points within each cluster, colored by cluster
            for cluster in unique_clusters:
                if cluster == -1:
                    cluster_color = ''  # Color for noise points
                else:
                    cluster_color = cols[cluster]
                
                cluster_morning_df = morning_df[morning_df[cluster_column] == cluster]
                
                for _, row in cluster_morning_df.iterrows():
                    popup_text = f"Date: {row['Date']}<br>Time: {row['Time']}<br>Elephant ID: {row['individual-local-identifier']}<br>Cluster: {cluster}"
                    folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=5,
                        color=cluster_color,
                        fill=True,
                        fill_color=cluster_color,
                        popup=popup_text
                    ).add_to(m)
            
            # Add cluster numbers as HTML div icons at the center of each cluster
            for cluster in unique_clusters:
                if cluster == -1:
                    continue  # Skip noise for numbering
                
                cluster_morning_df = morning_df[morning_df[cluster_column] == cluster]
                if cluster_morning_df.empty:
                    continue
                
                cluster_lat = cluster_morning_df['Latitude'].mean()
                cluster_lon = cluster_morning_df['Longitude'].mean()
                cluster_html = f"""<div style="font-size: 12pt; color: black; background-color: {cols[cluster]}; 
                                    width: 30px; height: 30px; display: flex; align-items: center; 
                                    justify-content: center; border-radius: 50%; border: 2px solid black;">
                                    {cluster}
                                    </div>"""

                icon = folium.DivIcon(html=cluster_html)
                folium.Marker(location=[cluster_lat, cluster_lon], icon=icon).add_to(m)
            
            # Save the map as HTML
            map_file = os.path.join(output_path, file_name.replace('.csv', '_morning_map.html'))
            m.save(map_file)
            print(f"Saved map: {map_file}")
        else:
            print(f"No data between 00:00:00 and 03:00:00 in {file_name}")