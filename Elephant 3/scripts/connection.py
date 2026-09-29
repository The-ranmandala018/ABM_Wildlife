# import pandas as pd
# import glob
# import numpy as np
# import os
# from datetime import datetime
# from math import radians, cos, sin, asin, sqrt

# def haversine_vectorized(lon1, lat1, lon2, lat2):
#     """
#     Vectorized haversine distance calculation.
#     """
#     lon1 = np.radians(lon1)
#     lat1 = np.radians(lat1)
#     lon2 = np.radians(lon2)
#     lat2 = np.radians(lat2)
#     dlon = lon2 - lon1[:, np.newaxis]
#     dlat = lat2 - lat1[:, np.newaxis]
#     a = (np.sin(dlat / 2)**2 + 
#          np.cos(lat1[:, np.newaxis]) * np.cos(lat2[np.newaxis, :]) * 
#          np.sin(dlon / 2)**2)
#     c = 2 * np.arcsin(np.sqrt(a))
#     r = 6371  # Radius of earth in kilometers
#     return c * r

# # Define paths
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis\connections'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')

# # Create connections directory if it doesn't exist
# os.makedirs(save_path, exist_ok=True)

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
#     exit()

# # Also add encoding to elephant files if needed
# ele_data_list = []
# for f in elephant_files:
#     try:
#         df = pd.read_csv(f, encoding='utf-8')
#     except UnicodeDecodeError:
#         df = pd.read_csv(f, encoding='latin-1')
    
#     # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#     filename = os.path.basename(f).replace('.csv', '')
#     elephant_id = filename.split('_')[0]
#     df['elephant_id'] = elephant_id  # Add as column
    
#     ele_data_list.append(df)

# ele_data = pd.concat(ele_data_list, ignore_index=True)

# # Clean column names
# ele_data.columns = ele_data.columns.str.strip()

# # If 'individual-local-identifier' exists, but use 'elephant_id' instead
# # Drop 'individual-local-identifier' if present, use elephant_id
# if 'individual-local-identifier' in ele_data.columns:
#     ele_data = ele_data.drop(columns=['individual-local-identifier'])

# # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
# # Handle possible column name variations
# time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
# ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])

# # Extract year, month, hour, and date
# ele_data['year'] = ele_data['DateTime'].dt.year
# ele_data['month'] = ele_data['DateTime'].dt.month
# ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
# ele_data['date'] = ele_data['DateTime'].dt.date

# # Load and integrate weather data (Temp_C, Precip_mm, Humidity_%)
# try:
#     weather = pd.read_csv(weather_path, encoding='utf-8')
# except UnicodeDecodeError:
#     weather = pd.read_csv(weather_path, encoding='latin-1')

# # Assume columns 'Date' (YYYY-MM-DD), 'Temp_C', 'Precip_mm', 'Humidity_%'
# weather['date'] = pd.to_datetime(weather['Date']).dt.date
# temp_dict = dict(zip(weather['date'], weather['Temp_C']))
# precip_dict = dict(zip(weather['date'], weather['Precip_mm']))
# humidity_dict = dict(zip(weather['date'], weather['Humidity_%']))
# ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
# ele_data['Precip_mm'] = ele_data['date'].map(precip_dict)
# ele_data['Humidity_%'] = ele_data['date'].map(humidity_dict)

# # Define radius for waterhole assignment (variable - change as needed)
# radius = 1.0  # km

# # Vectorized waterhole assignment
# print("Assigning waterholes to elephant observations (vectorized)...")
# ele_lons = ele_data['Longitude'].values
# ele_lats = ele_data['Latitude'].values
# wh_lons = waterholes['lon'].values
# wh_lats = waterholes['lat'].values

# # Compute distance matrix
# dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)

# # Find min dist and closest index for each elephant observation
# min_dists = np.min(dist_matrix, axis=1)
# closest_idxs = np.argmin(dist_matrix, axis=1)

# # Assign waterhole if within radius
# wh_names = waterholes['Name'].values
# ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)

# # Drop rows with no assigned waterhole or missing weather data
# ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C', 'Precip_mm', 'Humidity_%'])

# # Get unique individuals
# individuals = sorted(ele_data['elephant_id'].unique())

# # Process for each elephant and each year separately
# for ind in individuals:
#     ind_data = ele_data[ele_data['elephant_id'] == ind].copy()
#     unique_years = sorted(ind_data['year'].unique())
    
#     for year in unique_years:
#         year_data = ind_data[ind_data['year'] == year].copy()
#         if len(year_data) == 0:
#             continue
        
#         # Select relevant columns for connections analysis
#         connection_cols = ['elephant_id', 'DateTime', 'date', 'year', 'month', 'hour', 'Longitude', 'Latitude', 'waterhole', 'Temp_C', 'Precip_mm', 'Humidity_%']
#         year_connections = year_data[connection_cols].copy()
        
#         # Save separate CSV for this elephant-year
#         csv_filename = f'{ind}_{year}_connections.csv'
#         csv_path = os.path.join(save_path, csv_filename)
#         year_connections.to_csv(csv_path, index=False)
#         print(f"Saved connections CSV for {ind} - {year}: {csv_path}")

# print("All individual elephant-year connections CSV files saved to:", save_path)

#
# import pandas as pd
# import glob
# import numpy as np
# import os
# from datetime import datetime
# from math import radians, cos, sin, asin, sqrt

# def haversine_vectorized(lon1, lat1, lon2, lat2):
#     """
#     Vectorized haversine distance calculation.
#     """
#     lon1 = np.radians(lon1)
#     lat1 = np.radians(lat1)
#     lon2 = np.radians(lon2)
#     lat2 = np.radians(lat2)
#     dlon = lon2 - lon1[:, np.newaxis]
#     dlat = lat2 - lat1[:, np.newaxis]
#     a = (np.sin(dlat / 2)**2 + 
#          np.cos(lat1[:, np.newaxis]) * np.cos(lat2[np.newaxis, :]) * 
#          np.sin(dlon / 2)**2)
#     c = 2 * np.arcsin(np.sqrt(a))
#     r = 6371  # Radius of earth in kilometers
#     return c * r

# # Define paths
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis\connections'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')

# # Create connections directory if it doesn't exist
# os.makedirs(save_path, exist_ok=True)

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
#     exit()

# # Also add encoding to elephant files if needed
# ele_data_list = []
# for f in elephant_files:
#     try:
#         df = pd.read_csv(f, encoding='utf-8')
#     except UnicodeDecodeError:
#         df = pd.read_csv(f, encoding='latin-1')
    
#     # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#     filename = os.path.basename(f).replace('.csv', '')
#     elephant_id = filename.split('_')[0]
#     df['elephant_id'] = elephant_id  # Add as column
    
#     ele_data_list.append(df)

# ele_data = pd.concat(ele_data_list, ignore_index=True)

# # Clean column names
# ele_data.columns = ele_data.columns.str.strip()

# # If 'individual-local-identifier' exists, but use 'elephant_id' instead
# # Drop 'individual-local-identifier' if present, use elephant_id
# if 'individual-local-identifier' in ele_data.columns:
#     ele_data = ele_data.drop(columns=['individual-local-identifier'])

# # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
# # Handle possible column name variations
# time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
# ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])

# # Extract year, month, hour, and date
# ele_data['year'] = ele_data['DateTime'].dt.year
# ele_data['month'] = ele_data['DateTime'].dt.month
# ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
# ele_data['date'] = ele_data['DateTime'].dt.date

# # Load and integrate weather data (Temp_C, Precip_mm, Humidity_%)
# try:
#     weather = pd.read_csv(weather_path, encoding='utf-8')
# except UnicodeDecodeError:
#     weather = pd.read_csv(weather_path, encoding='latin-1')

# # Assume columns 'Date' (YYYY-MM-DD), 'Temp_C', 'Precip_mm', 'Humidity_%'
# weather['date'] = pd.to_datetime(weather['Date']).dt.date
# temp_dict = dict(zip(weather['date'], weather['Temp_C']))
# precip_dict = dict(zip(weather['date'], weather['Precip_mm']))
# humidity_dict = dict(zip(weather['date'], weather['Humidity_%']))
# ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
# ele_data['Precip_mm'] = ele_data['date'].map(precip_dict)
# ele_data['Humidity_%'] = ele_data['date'].map(humidity_dict)

# # Define radius for waterhole assignment (variable - change as needed)
# radius = 1.0  # km

# # Vectorized waterhole assignment
# print("Assigning waterholes to elephant observations (vectorized)...")
# ele_lons = ele_data['Longitude'].values
# ele_lats = ele_data['Latitude'].values
# wh_lons = waterholes['lon'].values
# wh_lats = waterholes['lat'].values

# # Compute distance matrix
# dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)

# # Find min dist and closest index for each elephant observation
# min_dists = np.min(dist_matrix, axis=1)
# closest_idxs = np.argmin(dist_matrix, axis=1)

# # Assign waterhole if within radius
# wh_names = waterholes['Name'].values
# ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)

# # Add waterhole longitude and latitude (for clarity, to distinguish from elephant's position)
# ele_data['waterhole_lon'] = np.where(min_dists <= radius, waterholes['lon'].iloc[closest_idxs], np.nan)
# ele_data['waterhole_lat'] = np.where(min_dists <= radius, waterholes['lat'].iloc[closest_idxs], np.nan)

# # Drop rows with no assigned waterhole or missing weather data
# ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C', 'Precip_mm', 'Humidity_%'])

# # Get unique individuals
# individuals = sorted(ele_data['elephant_id'].unique())

# # Process for each elephant and each year separately
# for ind in individuals:
#     ind_data = ele_data[ele_data['elephant_id'] == ind].copy()
#     unique_years = sorted(ind_data['year'].unique())
    
#     for year in unique_years:
#         year_data = ind_data[ind_data['year'] == year].copy()
#         if len(year_data) == 0:
#             continue
        
#         # Select relevant columns for connections analysis (elephant lon/lat, waterhole lon/lat)
#         connection_cols = ['elephant_id', 'DateTime', 'date', 'year', 'month', 'hour', 'Longitude', 'Latitude', 'waterhole_lon', 'waterhole_lat', 'waterhole', 'Temp_C', 'Precip_mm', 'Humidity_%']
#         year_connections = year_data[connection_cols].copy()
        
#         # Save separate CSV for this elephant-year
#         csv_filename = f'{ind}_{year}_connections.csv'
#         csv_path = os.path.join(save_path, csv_filename)
#         year_connections.to_csv(csv_path, index=False)
#         print(f"Saved connections CSV for {ind} - {year}: {csv_path}")

# print("All individual elephant-year connections CSV files saved to:", save_path)


import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

# Define paths
save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis\connections'
plots_dir = os.path.join(save_path, 'plots')
os.makedirs(plots_dir, exist_ok=True)

# Get all connection CSV files
connection_files = glob.glob(os.path.join(save_path, '*_connections.csv'))
if not connection_files:
    print("No connection CSV files found.")
    exit()

# Process each file separately
for file_path in connection_files:
    # Load data
    df = pd.read_csv(file_path)
    
    # Extract elephant_id and year from filename
    filename = os.path.basename(file_path).replace('.csv', '')
    elephant_id = filename.split('_')[0]
    year = filename.split('_')[1]
    
    # Create subplots for different variables (colors by Temp_C, Precip_mm, Humidity_%, hour, waterhole)
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'Elephant {elephant_id} - Year {year}: Movement Patterns on Map\nColored by Environmental & Temporal Factors', fontsize=16)
    
    # 1. Color by Temp_C
    scatter1 = axes[0, 0].scatter(df['Longitude'], df['Latitude'], c=df['Temp_C'], cmap='coolwarm', alpha=0.6, s=20)
    axes[0, 0].set_title('Colored by Temperature (°C)')
    axes[0, 0].set_xlabel('Longitude')
    axes[0, 0].set_ylabel('Latitude')
    plt.colorbar(scatter1, ax=axes[0, 0])
    
    # 2. Color by Precip_mm
    scatter2 = axes[0, 1].scatter(df['Longitude'], df['Latitude'], c=df['Precip_mm'], cmap='Blues', alpha=0.6, s=20)
    axes[0, 1].set_title('Colored by Precipitation (mm)')
    axes[0, 1].set_xlabel('Longitude')
    axes[0, 1].set_ylabel('Latitude')
    plt.colorbar(scatter2, ax=axes[0, 1])
    
    # 3. Color by Humidity_%
    scatter3 = axes[0, 2].scatter(df['Longitude'], df['Latitude'], c=df['Humidity_%'], cmap='viridis', alpha=0.6, s=20)
    axes[0, 2].set_title('Colored by Humidity (%)')
    axes[0, 2].set_xlabel('Longitude')
    axes[0, 2].set_ylabel('Latitude')
    plt.colorbar(scatter3, ax=axes[0, 2])
    
    # 4. Color by Hour (time of day)
    scatter4 = axes[1, 0].scatter(df['Longitude'], df['Latitude'], c=df['hour'], cmap='plasma', alpha=0.6, s=20)
    axes[1, 0].set_title('Colored by Time of Day (Hour)')
    axes[1, 0].set_xlabel('Longitude')
    axes[1, 0].set_ylabel('Latitude')
    plt.colorbar(scatter4, ax=axes[1, 0])
    
    # 5. Color by Waterhole (categorical, using hue)
    unique_wh = df['waterhole'].unique()
    colors_wh = plt.cm.Set3(np.linspace(0, 1, len(unique_wh)))
    for i, wh in enumerate(unique_wh):
        mask = df['waterhole'] == wh
        axes[1, 1].scatter(df[mask]['Longitude'], df[mask]['Latitude'], c=[colors_wh[i]], label=wh, alpha=0.7, s=30)
    axes[1, 1].set_title('Colored by Waterhole')
    axes[1, 1].set_xlabel('Longitude')
    axes[1, 1].set_ylabel('Latitude')
    axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 6. Combined: Size by Precip, Color by Temp (to show connections)
    scatter6 = axes[1, 2].scatter(df['Longitude'], df['Latitude'], c=df['Temp_C'], s=df['Precip_mm']*10 + 20, cmap='coolwarm', alpha=0.6)
    axes[1, 2].set_title('Size by Precip (mm), Color by Temp (°C)')
    axes[1, 2].set_xlabel('Longitude')
    axes[1, 2].set_ylabel('Latitude')
    plt.colorbar(scatter6, ax=axes[1, 2])
    
    plt.tight_layout()
    
    # Save plot
    plot_filename = f'{elephant_id}_{year}_connections_map.png'
    plot_path = os.path.join(plots_dir, plot_filename)
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved map plot for {elephant_id} - {year}: {plot_path}")

print("All map plots saved to:", plots_dir)


# .html interactive map generation
# import pandas as pd
# import glob
# import folium
# import os
# from folium import plugins
# import matplotlib.cm as cm

# # Define paths
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis\connections'
# html_dir = os.path.join(save_path, 'html_maps')
# os.makedirs(html_dir, exist_ok=True)

# # Get all connection CSV files
# connection_files = glob.glob(os.path.join(save_path, '*_connections.csv'))
# if not connection_files:
#     print("No connection CSV files found.")
#     exit()

# # Process each file separately
# for file_path in connection_files:
#     # Load data
#     df = pd.read_csv(file_path)
    
#     # Convert DateTime to datetime object
#     df['DateTime'] = pd.to_datetime(df['DateTime'])
    
#     # Extract elephant_id and year from filename
#     filename = os.path.basename(file_path).replace('.csv', '')
#     elephant_id = filename.split('_')[0]
#     year = filename.split('_')[1]
    
#     # Sort by DateTime for animation
#     df = df.sort_values('DateTime')
    
#     # Create base map centered on Etosha (approx center)
#     m = folium.Map(location=[-19.0, 15.5], zoom_start=8)
    
#     # Add static layers for factors (toggleable)
    
#     # 1. Layer: Color by Temp_C
#     temp_layer = folium.FeatureGroup(name='By Temperature (°C)', show=True)
#     for idx, row in df.iterrows():
#         folium.CircleMarker(
#             location=[row['Latitude'], row['Longitude']],
#             radius=3,
#             popup=f"Time: {row['DateTime']}<br>Temp: {row['Temp_C']}°C<br>Waterhole: {row['waterhole']}<br>Precip: {row['Precip_mm']}mm<br>Humidity: {row['Humidity_%']}%",
#             color='red' if row['Temp_C'] > 25 else 'blue',
#             fill=True,
#             fillColor='orange' if row['Temp_C'] > 25 else 'lightblue',
#             fillOpacity=0.7
#         ).add_to(temp_layer)
#     temp_layer.add_to(m)
    
#     # 2. Layer: Color by Precip_mm (size by precip)
#     precip_layer = folium.FeatureGroup(name='By Precipitation (mm)', show=False)
#     for idx, row in df.iterrows():
#         folium.CircleMarker(
#             location=[row['Latitude'], row['Longitude']],
#             radius=max(3, row['Precip_mm'] * 2),  # Size by precip
#             popup=f"Time: {row['DateTime']}<br>Precip: {row['Precip_mm']}mm<br>Waterhole: {row['waterhole']}<br>Temp: {row['Temp_C']}°C<br>Humidity: {row['Humidity_%']}%",
#             color='green',
#             fill=True,
#             fillColor='lightgreen',
#             fillOpacity=0.7
#         ).add_to(precip_layer)
#     precip_layer.add_to(m)
    
#     # 3. Layer: Color by Humidity_%
#     humidity_layer = folium.FeatureGroup(name='By Humidity (%)', show=False)
#     for idx, row in df.iterrows():
#         folium.CircleMarker(
#             location=[row['Latitude'], row['Longitude']],
#             radius=3,
#             popup=f"Time: {row['DateTime']}<br>Humidity: {row['Humidity_%']}%<br>Waterhole: {row['waterhole']}<br>Temp: {row['Temp_C']}°C<br>Precip: {row['Precip_mm']}mm",
#             color='purple' if row['Humidity_%'] > 60 else 'yellow',
#             fill=True,
#             fillColor='violet' if row['Humidity_%'] > 60 else 'gold',
#             fillOpacity=0.7
#         ).add_to(humidity_layer)
#     humidity_layer.add_to(m)
    
#     # 4. Layer: Color by Hour (time of day)
#     hour_layer = folium.FeatureGroup(name='By Time of Day (Hour)', show=False)
#     for idx, row in df.iterrows():
#         # Plasma colormap for hour (0-24 normalized to 0-1)
#         hour_norm = row['hour'] / 24.0
#         hour_color = cm.plasma(hour_norm)
#         color_hex = '#{:02x}{:02x}{:02x}'.format(int(hour_color[0]*255), int(hour_color[1]*255), int(hour_color[2]*255))
#         folium.CircleMarker(
#             location=[row['Latitude'], row['Longitude']],
#             radius=3,
#             popup=f"Time: {row['DateTime']}<br>Hour: {row['hour']:.1f}<br>Waterhole: {row['waterhole']}<br>Temp: {row['Temp_C']}°C",
#             color=color_hex,
#             fill=True,
#             fillColor=color_hex,
#             fillOpacity=0.7
#         ).add_to(hour_layer)
#     hour_layer.add_to(m)
    
#     # 5. Layer: By Waterhole (different colors per waterhole)
#     waterhole_layer = folium.FeatureGroup(name='By Waterhole', show=False)
#     unique_wh = df['waterhole'].unique()
#     colors_wh = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray', 'lightred']
#     for i, wh in enumerate(unique_wh):
#         mask = df['waterhole'] == wh
#         wh_color = colors_wh[i % len(colors_wh)]
#         for idx, row in df[mask].iterrows():
#             folium.CircleMarker(
#                 location=[row['Latitude'], row['Longitude']],
#                 radius=5,
#                 popup=f"Time: {row['DateTime']}<br>Waterhole: {wh}<br>Temp: {row['Temp_C']}°C, Precip: {row['Precip_mm']}mm, Humidity: {row['Humidity_%']}%",
#                 color=wh_color,
#                 fill=True,
#                 fillColor=wh_color,
#                 fillOpacity=0.7
#             ).add_to(waterhole_layer)
#     waterhole_layer.add_to(m)
    
#     # Time Animation Layer: Points appear chronologically by DateTime (add directly to map)
#     features = []
#     for idx, row in df.iterrows():
#         feature = {
#             'type': 'Feature',
#             'geometry': {
#                 'type': 'Point',
#                 'coordinates': [row['Longitude'], row['Latitude']]
#             },
#             'properties': {
#                 'times': [row['DateTime'].isoformat()],  # Timestamp for this point
#                 'style': {
#                     'color': 'blue',
#                     'radius': 3,
#                     'fillOpacity': 0.7
#                 },
#                 'popup': f"Time: {row['DateTime']}<br>Waterhole: {row['waterhole']}<br>Temp: {row['Temp_C']}°C<br>Precip: {row['Precip_mm']}mm<br>Humidity: {row['Humidity_%']}%"
#             }
#         }
#         features.append(feature)
    
#     time_geojson = {
#         'type': 'FeatureCollection',
#         'features': features
#     }
    
#     # Add TimestampedGeoJson directly to the map (not to a FeatureGroup)
#     plugins.TimestampedGeoJson(time_geojson,
#                               period='P1D',  # Daily period
#                               add_last_point=True,
#                               auto_play=False,
#                               loop=False,
#                               max_speed=10,
#                               loop_button=True,
#                               date_options='YYYY/MM/DD HH:MM:SS',
#                               time_slider_drag_update=True
#     ).add_to(m)
    
#     # Add layer control
#     folium.LayerControl().add_to(m)
    
#     # Save HTML map
#     html_filename = f'{elephant_id}_{year}_connections_map.html'
#     html_path = os.path.join(html_dir, html_filename)
#     m.save(html_path)
#     print(f"Saved interactive HTML map for {elephant_id} - {year}: {html_path}")

# print("All interactive HTML maps saved to:", html_dir)