# polar plot : A graph that displays data in polar coordinates, where points are defined by a radius (\(r\)) and an angle (\(\theta \))

# import pandas as pd
# import glob
# import matplotlib.pyplot as plt
# import numpy as np
# import seaborn as sns
# from datetime import datetime
# import os
# from math import radians, cos, sin, asin, sqrt

# def haversine_vectorized(lon1, lat1, lon2, lat2):
#     """
#     Vectorized haversine distance calculation.
#     lon1, lat1: arrays of shape (M,)
#     lon2, lat2: arrays of shape (K,)
#     Returns distance matrix of shape (M, K)
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

# # Define paths (adjust if needed for exact file structure)
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# plots_dir = os.path.join(base_path, 'analysis', 'plots1')

# # Create plots directory if it doesn't exist
# os.makedirs(plots_dir, exist_ok=True)

# # Set seaborn style for clearer plots
# sns.set_style("whitegrid")

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
# else:
#     # Also add encoding to elephant files if needed
#     ele_data_list = []
#     for f in elephant_files:
#         try:
#             df = pd.read_csv(f, encoding='utf-8')
#         except UnicodeDecodeError:
#             df = pd.read_csv(f, encoding='latin-1')
        
#         # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#         filename = os.path.basename(f).replace('.csv', '')
#         elephant_id = filename.split('_')[0]
#         df['elephant_id'] = elephant_id  # Add as column
        
#         ele_data_list.append(df)
    
#     ele_data = pd.concat(ele_data_list, ignore_index=True)
    
#     # Clean column names
#     ele_data.columns = ele_data.columns.str.strip()
    
#     # Drop old ID column if exists
#     if 'individual-local-identifier' in ele_data.columns:
#         ele_data = ele_data.drop(columns=['individual-local-identifier'])
    
#     # Parse DateTime
#     time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
#     ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
    
#     # Extract date/time features
#     ele_data['year'] = ele_data['DateTime'].dt.year
#     ele_data['month'] = ele_data['DateTime'].dt.month
#     ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
    
#     # Define radius (km)
#     radius = 1.0  
    
#     # Vectorized waterhole assignment
#     print("Assigning waterholes to elephant observations (vectorized)...")
#     ele_lons = ele_data['Longitude'].values
#     ele_lats = ele_data['Latitude'].values
#     wh_lons = waterholes['lon'].values
#     wh_lats = waterholes['lat'].values
    
#     dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
#     min_dists = np.min(dist_matrix, axis=1)
#     closest_idxs = np.argmin(dist_matrix, axis=1)
    
#     wh_names = waterholes['Name'].values
#     ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
#     ele_data = ele_data.dropna(subset=['waterhole'])
    
#     # Category setup
#     waterholes_list = sorted(waterholes['Name'].unique())
#     ele_data['wh_cat'] = pd.Categorical(ele_data['waterhole'], categories=waterholes_list)
#     ele_data['month_cat'] = pd.Categorical(ele_data['month'], categories=range(1, 13))
    
#     individuals = sorted(ele_data['elephant_id'].unique())
#     print(f"Processing {len(individuals)} individuals...")

#     # === Polar Clock Plot with Month Colors and Waterhole Info ===
# for ind in individuals:
#     ind_data = ele_data[ele_data['elephant_id'] == ind]
#     years = sorted(ind_data['year'].unique())

#     for year in years:
#         year_data = ind_data[ind_data['year'] == year]
#         if len(year_data) == 0:
#             continue

#         # Create polar plot
#         fig = plt.figure(figsize=(9, 9))
#         ax = plt.subplot(111, polar=True)

#         # Define month colors (Jan=1 to Dec=12)
#         month_colors = plt.cm.hsv(np.linspace(0, 1, 12))

#         # Plot by month and waterhole
#         for m in sorted(year_data['month'].unique()):
#             month_data = year_data[year_data['month'] == m]
#             color = month_colors[m-1]
#             month_name = datetime(1900, m, 1).strftime('%b')

#             # Plot each waterhole in that month
#             for wh in sorted(month_data['waterhole'].unique()):
#                 wh_data = month_data[month_data['waterhole'] == wh]
#                 hours_rad = 2 * np.pi * (wh_data['hour'] / 24)

#                 # Plot as small scatter points (each point = one visit)
#                 ax.scatter(
#                     hours_rad,
#                     np.full_like(hours_rad, fill_value=m, dtype=float),  # month on radius
#                     label=f'{month_name} - {wh}',
#                     color=color,
#                     alpha=0.7,
#                     s=25
#                 )

#         # Polar clock setup
#         ax.set_theta_zero_location("N")   # 0h at top
#         ax.set_theta_direction(-1)        # Clockwise
#         ax.set_xticks(np.linspace(0, 2*np.pi, 24, endpoint=False))
#         ax.set_xticklabels(range(24))
#         ax.set_rgrids(range(1, 13), labels=[datetime(1900, m, 1).strftime('%b') for m in range(1, 13)], angle=0)
#         ax.set_title(f'Elephant {ind} - Year {year}\nTime-of-Day vs Waterhole (by Month)', fontsize=14, pad=20)

#         # Add legend (compact)
#         ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.05), fontsize=8, frameon=False)

#         plt.tight_layout()

#         # Save the figure
#         save_path = os.path.join(plots_dir, f'{ind}_{year}_polar_monthcolor_waterhole.png')
#         plt.savefig(save_path, dpi=150, bbox_inches='tight')
#         plt.close()
#         print(f"Saved polar plot with month colors and waterholes: {save_path}")


# # Scatter Plot with Month Colors and Waterhole Info

# import pandas as pd
# import glob
# import matplotlib.pyplot as plt
# import numpy as np
# import seaborn as sns
# from datetime import datetime
# import os
# from math import radians, cos, sin, asin, sqrt
# import xml.etree.ElementTree as ET
# from xml.dom import minidom

# def haversine_vectorized(lon1, lat1, lon2, lat2):
#     """
#     Vectorized haversine distance calculation.
#     lon1, lat1: arrays of shape (M,)
#     lon2, lat2: arrays of shape (K,)
#     Returns distance matrix of shape (M, K)
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

# # Define paths (adjust if needed for exact file structure)
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# plots_dir = os.path.join(save_path, 'analysis', 'plots1')

# # Create plots directory if it doesn't exist
# os.makedirs(plots_dir, exist_ok=True)

# # Set seaborn style for clearer plots
# sns.set_style("whitegrid")

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
# else:
#     # Also add encoding to elephant files if needed
#     ele_data_list = []
#     for f in elephant_files:
#         try:
#             df = pd.read_csv(f, encoding='utf-8')
#         except UnicodeDecodeError:
#             df = pd.read_csv(f, encoding='latin-1')
        
#         # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#         filename = os.path.basename(f).replace('.csv', '')
#         elephant_id = filename.split('_')[0]
#         df['elephant_id'] = elephant_id  # Add as column
        
#         ele_data_list.append(df)
    
#     ele_data = pd.concat(ele_data_list, ignore_index=True)
    
#     # Clean column names
#     ele_data.columns = ele_data.columns.str.strip()
    
#     # If 'individual-local-identifier' exists, but use 'elephant_id' instead
#     # Drop 'individual-local-identifier' if present, use elephant_id
#     if 'individual-local-identifier' in ele_data.columns:
#         ele_data = ele_data.drop(columns=['individual-local-identifier'])
    
#     # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
#     # Handle possible column name variations
#     time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
#     ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
    
#     # Extract year, month, and fractional hour for plotting
#     ele_data['year'] = ele_data['DateTime'].dt.year
#     ele_data['month'] = ele_data['DateTime'].dt.month
#     ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
    
#     # Define radius (variable - change as needed)
#     radius = 1.0  # km
    
#     # Vectorized waterhole assignment
#     print("Assigning waterholes to elephant observations (vectorized)...")
#     ele_lons = ele_data['Longitude'].values
#     ele_lats = ele_data['Latitude'].values
#     wh_lons = waterholes['lon'].values
#     wh_lats = waterholes['lat'].values
    
#     # Compute distance matrix
#     dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
    
#     # Find min dist and closest index for each elephant observation
#     min_dists = np.min(dist_matrix, axis=1)
#     closest_idxs = np.argmin(dist_matrix, axis=1)
    
#     # Assign waterhole if within radius
#     wh_names = waterholes['Name'].values
#     ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
    
#     # Drop rows with no assigned waterhole
#     ele_data = ele_data.dropna(subset=['waterhole'])
    
#     # Get sorted unique waterhole names for x-axis
#     waterholes_list = sorted(waterholes['Name'].unique())
    
#     # Create categorical for waterholes and months
#     ele_data['wh_cat'] = pd.Categorical(ele_data['waterhole'], categories=waterholes_list)
#     ele_data['month_cat'] = pd.Categorical(ele_data['month'], categories=range(1,13))
    
#     # Get unique individuals (now using true elephant_id prefix)
#     individuals = sorted(ele_data['elephant_id'].unique())
    
#     print(f"Processing {len(individuals)} individuals...")
    
#     # Define colors for months (KML ABGR hex, e.g., ff0000ff for red)
#     month_colors = {
#         1: 'ff0000ff',  # Red
#         2: 'ff00ff00',  # Green
#         3: 'ff0000ff',  # Blue wait, ff00ffff cyan
#         4: 'ffff0000',  # Yellow
#         5: 'ff0000ff',  # Magenta ff00ff00 wait, adjust
#         6: 'ffffff00',  # Cyan
#         7: 'ffff00ff',  # Magenta
#         8: 'ff00ffff',  # Yellow wait, better cycle
#         9: 'ff8080ff',  # Light blue
#         10: 'ff80ffff', # Light green
#         11: 'ffff80ff', # Light red
#         12: 'ffffff80'  # Light yellow
#     }
#     # Better distinct colors
#     colors_list = ['ff0000ff', 'ff00ff00', 'ffff0000', 'ff00ffff', 'ffff00ff', 'ff808080', 'ff8000ff', 'ff0080ff', 'ff80ff00', 'ffff8000', 'ff008000', 'ff800000']
#     month_colors = {i+1: colors_list[i % len(colors_list)] for i in range(12)}
    
#     # Only process for 2010
#     target_year = 2010
    
#     for ind in individuals:
#         ind_data = ele_data[ele_data['elephant_id'] == ind]
#         if target_year not in ind_data['year'].values:
#             continue
        
#         year_data = ind_data[ind_data['year'] == target_year]
        
#         if len(year_data) == 0:
#             continue
        
#         # Create CSV: lon, lat, waterhole, month
#         csv_data = year_data[['Longitude', 'Latitude', 'waterhole', 'month']].copy()
#         csv_data.columns = ['lon', 'lat', 'waterhole', 'month']
#         csv_path = os.path.join(plots_dir, f'{ind}_{target_year}_waterhole_visits.csv')
#         csv_data.to_csv(csv_path, index=False)
#         print(f"Saved CSV: {csv_path}")
        
#         # Create KML for Google Earth
#         kml = ET.Element('kml', xmlns='http://www.opengis.net/kml/2.2')
#         document = ET.SubElement(kml, 'Document')
#         ET.SubElement(document, 'name').text = f'Elephant {ind} - 2010 Waterhole Visits'
#         ET.SubElement(document, 'description').text = f'Points colored by month for elephant {ind} in 2010'
        
#         # Create styles for each month
#         for month in range(1, 13):
#             style_id = f'month{month}_style'
#             style = ET.SubElement(document, 'Style', id=style_id)
#             icon_style = ET.SubElement(style, 'IconStyle')
#             ET.SubElement(icon_style, 'color').text = month_colors.get(month, 'ff000000')
#             icon = ET.SubElement(icon_style, 'Icon')
#             ET.SubElement(icon, 'href').text = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
#             label_style = ET.SubElement(style, 'LabelStyle')
#             ET.SubElement(label_style, 'color').text = month_colors.get(month, 'ff000000')
        
#         # Create folder for points
#         folder = ET.SubElement(document, 'Folder')
#         ET.SubElement(folder, 'name').text = 'Waterhole Visits'
#         ET.SubElement(folder, 'description').text = 'Each point represents an observation at a waterhole, colored by month'
        
#         # Add placemarks
#         for _, row in year_data.iterrows():
#             placemark = ET.SubElement(folder, 'Placemark')
#             name = ET.SubElement(placemark, 'name')
#             name.text = f"{row['waterhole']} - Month {int(row['month'])}"
#             desc = ET.SubElement(placemark, 'description')
#             desc.text = f"Waterhole: {row['waterhole']}, Month: {int(row['month'])}, Time: {row['DateTime']}, Lon: {row['Longitude']:.6f}, Lat: {row['Latitude']:.6f}"
#             style_url = ET.SubElement(placemark, 'styleUrl')
#             style_url.text = f'#month{int(row["month"])}_style'
#             point = ET.SubElement(placemark, 'Point')
#             coordinates = ET.SubElement(point, 'coordinates')
#             coordinates.text = f"{row['Longitude']:.6f},{row['Latitude']:.6f},0"
        
#         # Write KML
#         rough_string = ET.tostring(kml, 'unicode')
#         reparsed = minidom.parseString(rough_string)
#         pretty_kml = reparsed.toprettyxml(indent="  ")
#         kml_path = os.path.join(plots_dir, f'{ind}_{target_year}_waterhole_visits.kml')
#         with open(kml_path, 'w', encoding='utf-8') as f:
#             f.write(pretty_kml)
#         print(f"Saved KML: {kml_path}")
    
#     # Original plotting code (for all years, unchanged)
#     for ind in individuals:
#         ind_data = ele_data[ele_data['elephant_id'] == ind]
#         years = sorted(ind_data['year'].unique())
        
#         for year in years:
#             year_data = ind_data[ind_data['year'] == year]
            
#             if len(year_data) == 0:
#                 continue
            
#             # Create single figure for the year with all months
#             fig, ax = plt.subplots(figsize=(16, 10))
            
#             # Use seaborn stripplot for clearer, non-overlapping scatter (jittered)
#             sns.stripplot(data=year_data, x='wh_cat', y='hour', hue='month_cat', 
#                           ax=ax, alpha=0.7, size=6, dodge=True, jitter=0.2)
            
#             # Add grid lines for better identification of waterholes
#             ax.grid(True, which='major', axis='x', linestyle='-', alpha=0.5, linewidth=1.0)
#             ax.grid(True, which='major', axis='y', linestyle='-', alpha=0.3, linewidth=0.5)
            
#             ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
#             ax.set_xlabel('Waterhole', fontsize=12)
#             ax.set_ylim(0, 24)
#             ax.set_ylabel('Time (24h)', fontsize=12)
#             ax.set_title(f'Elephant {ind} - Year {year} (Radius: {radius} km)', fontsize=16)
#             ax.legend(title='Month', bbox_to_anchor=(1.05, 1), loc='upper left')
            
#             plt.tight_layout()
            
#             # Save plot with simplified name
#             save_path = os.path.join(plots_dir, f'{ind}_{year}.png')
#             plt.savefig(save_path, dpi=150, bbox_inches='tight')
#             plt.close()
            
#             print(f"Saved: {save_path}")
    
#     print("Plotting complete. All figures saved to:", plots_dir)
#     print("CSV and KML files for 2010 saved to:", plots_dir)


# import pandas as pd
# import glob
# import numpy as np
# import os
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
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

# # Define paths (adjust if needed for exact file structure)
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')
# plots_dir = os.path.join(save_path, 'analysis', 'plots2')

# # Create plots directory if it doesn't exist
# os.makedirs(plots_dir, exist_ok=True)

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
# else:
#     # Also add encoding to elephant files if needed
#     ele_data_list = []
#     for f in elephant_files:
#         try:
#             df = pd.read_csv(f, encoding='utf-8')
#         except UnicodeDecodeError:
#             df = pd.read_csv(f, encoding='latin-1')
        
#         # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#         filename = os.path.basename(f).replace('.csv', '')
#         elephant_id = filename.split('_')[0]
#         df['elephant_id'] = elephant_id  # Add as column
        
#         ele_data_list.append(df)
    
#     ele_data = pd.concat(ele_data_list, ignore_index=True)
    
#     # Clean column names
#     ele_data.columns = ele_data.columns.str.strip()
    
#     # If 'individual-local-identifier' exists, but use 'elephant_id' instead
#     # Drop 'individual-local-identifier' if present, use elephant_id
#     if 'individual-local-identifier' in ele_data.columns:
#         ele_data = ele_data.drop(columns=['individual-local-identifier'])
    
#     # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
#     # Handle possible column name variations
#     time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
#     ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
    
#     # Extract year, month, and fractional hour for plotting
#     ele_data['year'] = ele_data['DateTime'].dt.year
#     ele_data['month'] = ele_data['DateTime'].dt.month
#     ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
#     ele_data['date'] = ele_data['DateTime'].dt.date
    
#     # Load and integrate weather data
#     try:
#         weather = pd.read_csv(weather_path, encoding='utf-8')
#     except UnicodeDecodeError:
#         weather = pd.read_csv(weather_path, encoding='latin-1')
    
#     # Assume columns 'Date' (YYYY-MM-DD) and 'Temp_C'
#     weather['date'] = pd.to_datetime(weather['Date']).dt.date
#     temp_dict = dict(zip(weather['date'], weather['Temp_C']))
#     ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
    
#     # Define radius (variable - change as needed)
#     radius = 1.0  # km
    
#     # Vectorized waterhole assignment
#     print("Assigning waterholes to elephant observations (vectorized)...")
#     ele_lons = ele_data['Longitude'].values
#     ele_lats = ele_data['Latitude'].values
#     wh_lons = waterholes['lon'].values
#     wh_lats = waterholes['lat'].values
    
#     # Compute distance matrix
#     dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
    
#     # Find min dist and closest index for each elephant observation
#     min_dists = np.min(dist_matrix, axis=1)
#     closest_idxs = np.argmin(dist_matrix, axis=1)
    
#     # Assign waterhole if within radius
#     wh_names = waterholes['Name'].values
#     ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
    
#     # Drop rows with no assigned waterhole or missing Temp_C
#     ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C'])
    
#     # Get sorted unique waterhole names for x-axis
#     waterholes_list = sorted(waterholes['Name'].unique())
    
#     # Create categorical for waterholes and months
#     ele_data['wh_cat'] = pd.Categorical(ele_data['waterhole'], categories=waterholes_list)
#     ele_data['month_cat'] = pd.Categorical(ele_data['month'], categories=range(1,13))
    
#     # Get unique individuals (now using true elephant_id prefix)
#     individuals = sorted(ele_data['elephant_id'].unique())
    
#     print(f"Processing {len(individuals)} individuals...")
    
#     # Process for all years
#     all_clustered_data = []
#     unique_years = sorted(ele_data['year'].unique())
    
#     for year in unique_years:
#         year_data = ele_data[ele_data['year'] == year].copy()
#         if len(year_data) == 0:
#             continue
        
#         year_data['waterhole_cat'] = pd.Categorical(year_data['waterhole'])
        
#         # Prepare for clustering: features - hour, Temp_C, waterhole (one-hot)
#         features = ['hour', 'Temp_C']
#         categorical_features = ['waterhole']
#         preprocessor = ColumnTransformer(
#             transformers=[
#                 ('num', StandardScaler(), features),
#                 ('cat', OneHotEncoder(), categorical_features)
#             ])
        
#         X = preprocessor.fit_transform(year_data[features + categorical_features])
        
#         # KMeans with 5 clusters (adjustable)
#         kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
#         year_data['cluster'] = kmeans.fit_predict(X)
        
#         # Group by cluster to find start/end times (min/max DateTime per cluster per elephant)
#         clustered_data = year_data[['elephant_id', 'Longitude', 'Latitude', 'DateTime', 'date', 'year', 'hour', 'waterhole', 'Temp_C', 'cluster']].copy()
#         clustered_data['time'] = clustered_data['DateTime'].dt.time
#         clustered_data['start_time'] = clustered_data.groupby(['elephant_id', 'cluster'])['DateTime'].transform('min')
#         clustered_data['end_time'] = clustered_data.groupby(['elephant_id', 'cluster'])['DateTime'].transform('max')
#         clustered_data['start_time_str'] = clustered_data['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
#         clustered_data['end_time_str'] = clustered_data['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
#         # Select columns for CSV
#         output_cols = ['elephant_id', 'Longitude', 'Latitude', 'time', 'date', 'year', 'cluster', 'start_time_str', 'end_time_str', 'hour', 'waterhole', 'Temp_C']
#         clustered_data = clustered_data[output_cols]
        
#         all_clustered_data.append(clustered_data)
        
#         print(f"Processed year {year}")
    
#     # Combine all years
#     final_clustered_data = pd.concat(all_clustered_data, ignore_index=True)
    
#     # Save CSV
#     csv_path = os.path.join(plots_dir, 'elephant_waterhole_clusters_all_years.csv')
#     final_clustered_data.to_csv(csv_path, index=False)
#     print(f"CSV saved to: {csv_path}")
    
#     # Print preview
#     print(final_clustered_data.head(10))

# import pandas as pd
# import glob
# import numpy as np
# import os
# from sklearn.cluster import SpectralClustering
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler as Scaler
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

# # Define paths (adjust if needed for exact file structure)
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')
# plots_dir = os.path.join(save_path, 'analysis', 'plots2')

# # Create plots directory if it doesn't exist
# os.makedirs(plots_dir, exist_ok=True)

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
# else:
#     # Also add encoding to elephant files if needed
#     ele_data_list = []
#     for f in elephant_files:
#         try:
#             df = pd.read_csv(f, encoding='utf-8')
#         except UnicodeDecodeError:
#             df = pd.read_csv(f, encoding='latin-1')
        
#         # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#         filename = os.path.basename(f).replace('.csv', '')
#         elephant_id = filename.split('_')[0]
#         df['elephant_id'] = elephant_id  # Add as column
        
#         ele_data_list.append(df)
    
#     ele_data = pd.concat(ele_data_list, ignore_index=True)
    
#     # Clean column names
#     ele_data.columns = ele_data.columns.str.strip()
    
#     # If 'individual-local-identifier' exists, but use 'elephant_id' instead
#     # Drop 'individual-local-identifier' if present, use elephant_id
#     if 'individual-local-identifier' in ele_data.columns:
#         ele_data = ele_data.drop(columns=['individual-local-identifier'])
    
#     # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
#     # Handle possible column name variations
#     time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
#     ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
    
#     # Extract year, month, and fractional hour for plotting
#     ele_data['year'] = ele_data['DateTime'].dt.year
#     ele_data['month'] = ele_data['DateTime'].dt.month
#     ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
#     ele_data['date'] = ele_data['DateTime'].dt.date
    
#     # Load and integrate weather data
#     try:
#         weather = pd.read_csv(weather_path, encoding='utf-8')
#     except UnicodeDecodeError:
#         weather = pd.read_csv(weather_path, encoding='latin-1')
    
#     # Assume columns 'Date' (YYYY-MM-DD) and 'Temp_C'
#     weather['date'] = pd.to_datetime(weather['Date']).dt.date
#     temp_dict = dict(zip(weather['date'], weather['Temp_C']))
#     ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
    
#     # Define radius (variable - change as needed)
#     radius = 1.0  # km
    
#     # Vectorized waterhole assignment
#     print("Assigning waterholes to elephant observations (vectorized)...")
#     ele_lons = ele_data['Longitude'].values
#     ele_lats = ele_data['Latitude'].values
#     wh_lons = waterholes['lon'].values
#     wh_lats = waterholes['lat'].values
    
#     # Compute distance matrix
#     dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
    
#     # Find min dist and closest index for each elephant observation
#     min_dists = np.min(dist_matrix, axis=1)
#     closest_idxs = np.argmin(dist_matrix, axis=1)
    
#     # Assign waterhole if within radius
#     wh_names = waterholes['Name'].values
#     ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
    
#     # Drop rows with no assigned waterhole or missing Temp_C
#     ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C'])
    
#     # Get sorted unique waterhole names for x-axis
#     waterholes_list = sorted(waterholes['Name'].unique())
    
#     # Create categorical for waterholes and months
#     ele_data['wh_cat'] = pd.Categorical(ele_data['waterhole'], categories=waterholes_list)
#     ele_data['month_cat'] = pd.Categorical(ele_data['month'], categories=range(1,13))
    
#     # Get unique individuals (now using true elephant_id prefix)
#     individuals = sorted(ele_data['elephant_id'].unique())
    
#     print(f"Processing {len(individuals)} individuals...")
    
#     # Data-driven seasonal pattern identification
#     # Compute monthly average temperature across all years
#     monthly_avg_temp = ele_data.groupby('month')['Temp_C'].mean().reset_index()
    
#     # Use KMeans to cluster months into 4 seasons based on avg temp
#     scaler = Scaler()
#     monthly_temp_scaled = scaler.fit_transform(monthly_avg_temp[['Temp_C']])
#     kmeans_seasons = KMeans(n_clusters=4, random_state=42, n_init=10)
#     monthly_avg_temp['season_cluster'] = kmeans_seasons.fit_predict(monthly_temp_scaled)
    
#     # Assign season labels based on clusters (sorted by avg temp)
#     season_labels = {0: 'Cold Dry', 1: 'Semi-Cold Dry', 2: 'Warm Wet', 3: 'Hot Wet'}  # Adjust labels based on temp ranges
#     # Sort clusters by mean temp for logical labeling
#     cluster_means = monthly_avg_temp.groupby('season_cluster')['Temp_C'].mean().sort_values()
#     sorted_clusters = cluster_means.index.tolist()
#     season_mapping = {}
#     for i, cluster in enumerate(sorted_clusters):
#         if i == 0:
#             season_mapping[cluster] = 'Cold Dry'
#         elif i == 1:
#             season_mapping[cluster] = 'Semi-Cold Dry'
#         elif i == 2:
#             season_mapping[cluster] = 'Warm Semi-Wet'
#         else:
#             season_mapping[cluster] = 'Hot Wet'
    
#     monthly_avg_temp['season'] = monthly_avg_temp['season_cluster'].map(season_mapping)
#     month_to_season = dict(zip(monthly_avg_temp['month'], monthly_avg_temp['season']))
    
#     # Add season to ele_data
#     ele_data['season'] = ele_data['month'].map(month_to_season)
    
#     print("Identified seasonal patterns:", month_to_season)
    
#     # Process for all years
#     all_clustered_data = []
#     unique_years = sorted(ele_data['year'].unique())
    
#     for year in unique_years:
#         year_data = ele_data[ele_data['year'] == year].copy()
#         if len(year_data) == 0:
#             continue
        
#         year_data['waterhole_cat'] = pd.Categorical(year_data['waterhole'])
        
#         # Prepare for clustering: features - hour, Temp_C, waterhole (one-hot)
#         features = ['hour', 'Temp_C']
#         categorical_features = ['waterhole']
#         preprocessor = ColumnTransformer(
#             transformers=[
#                 ('num', StandardScaler(), features),
#                 ('cat', OneHotEncoder(), categorical_features)
#             ])
        
#         X = preprocessor.fit_transform(year_data[features + categorical_features])
        
#         # Spectral Clustering with 5 clusters (adjustable)
#         spectral = SpectralClustering(n_clusters=5, random_state=42, affinity='rbf')
#         year_data['cluster'] = spectral.fit_predict(X)
        
#         # Group by cluster to find start/end times (min/max DateTime per cluster per elephant)
#         clustered_data = year_data[['elephant_id', 'Longitude', 'Latitude', 'DateTime', 'date', 'year', 'hour', 'waterhole', 'Temp_C', 'cluster', 'season']].copy()
#         clustered_data['time'] = clustered_data['DateTime'].dt.time
#         clustered_data['start_time'] = clustered_data.groupby(['elephant_id', 'cluster'])['DateTime'].transform('min')
#         clustered_data['end_time'] = clustered_data.groupby(['elephant_id', 'cluster'])['DateTime'].transform('max')
#         clustered_data['start_time_str'] = clustered_data['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
#         clustered_data['end_time_str'] = clustered_data['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
#         # Select columns for CSV (now including season)
#         output_cols = ['elephant_id', 'Longitude', 'Latitude', 'time', 'date', 'year', 'cluster', 'start_time_str', 'end_time_str', 'hour', 'waterhole', 'Temp_C', 'season']
#         clustered_data = clustered_data[output_cols]
        
#         all_clustered_data.append(clustered_data)
        
#         print(f"Processed year {year}")
    
#     # Combine all years
#     final_clustered_data = pd.concat(all_clustered_data, ignore_index=True)
    
#     # Save CSV
#     csv_path = os.path.join(plots_dir, 'elephant_waterhole_clusters_spectral_all_years_with_seasons.csv')
#     final_clustered_data.to_csv(csv_path, index=False)
#     print(f"CSV saved to: {csv_path}")
    
#     # Print preview
#     print(final_clustered_data.head(10))

# import pandas as pd
# import glob
# import numpy as np
# import os
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
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

# # Define paths (adjust if needed for exact file structure)
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')
# plots_dir = os.path.join(save_path, 'analysis', 'plots2')

# # Create plots directory if it doesn't exist
# os.makedirs(plots_dir, exist_ok=True)

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
# else:
#     # Also add encoding to elephant files if needed
#     ele_data_list = []
#     for f in elephant_files:
#         try:
#             df = pd.read_csv(f, encoding='utf-8')
#         except UnicodeDecodeError:
#             df = pd.read_csv(f, encoding='latin-1')
        
#         # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#         filename = os.path.basename(f).replace('.csv', '')
#         elephant_id = filename.split('_')[0]
#         df['elephant_id'] = elephant_id  # Add as column
        
#         ele_data_list.append(df)
    
#     ele_data = pd.concat(ele_data_list, ignore_index=True)
    
#     # Clean column names
#     ele_data.columns = ele_data.columns.str.strip()
    
#     # If 'individual-local-identifier' exists, but use 'elephant_id' instead
#     # Drop 'individual-local-identifier' if present, use elephant_id
#     if 'individual-local-identifier' in ele_data.columns:
#         ele_data = ele_data.drop(columns=['individual-local-identifier'])
    
#     # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
#     # Handle possible column name variations
#     time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
#     ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
    
#     # Extract year, month, and fractional hour for plotting
#     ele_data['year'] = ele_data['DateTime'].dt.year
#     ele_data['month'] = ele_data['DateTime'].dt.month
#     ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
#     ele_data['date'] = ele_data['DateTime'].dt.date
    
#     # Load and integrate weather data
#     try:
#         weather = pd.read_csv(weather_path, encoding='utf-8')
#     except UnicodeDecodeError:
#         weather = pd.read_csv(weather_path, encoding='latin-1')
    
#     # Assume columns 'Date' (YYYY-MM-DD) and 'Temp_C'
#     weather['date'] = pd.to_datetime(weather['Date']).dt.date
#     temp_dict = dict(zip(weather['date'], weather['Temp_C']))
#     ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
    
#     # Define radius (variable - change as needed)
#     radius = 1.0  # km
    
#     # Vectorized waterhole assignment
#     print("Assigning waterholes to elephant observations (vectorized)...")
#     ele_lons = ele_data['Longitude'].values
#     ele_lats = ele_data['Latitude'].values
#     wh_lons = waterholes['lon'].values
#     wh_lats = waterholes['lat'].values
    
#     # Compute distance matrix
#     dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
    
#     # Find min dist and closest index for each elephant observation
#     min_dists = np.min(dist_matrix, axis=1)
#     closest_idxs = np.argmin(dist_matrix, axis=1)
    
#     # Assign waterhole if within radius
#     wh_names = waterholes['Name'].values
#     ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
    
#     # Drop rows with no assigned waterhole or missing Temp_C
#     ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C'])
    
#     # Get sorted unique waterhole names for x-axis
#     waterholes_list = sorted(waterholes['Name'].unique())
    
#     # Create categorical for waterholes and months
#     ele_data['wh_cat'] = pd.Categorical(ele_data['waterhole'], categories=waterholes_list)
#     ele_data['month_cat'] = pd.Categorical(ele_data['month'], categories=range(1,13))
    
#     # Get unique individuals (now using true elephant_id prefix)
#     individuals = sorted(ele_data['elephant_id'].unique())
    
#     print(f"Processing {len(individuals)} individuals...")
    
#     # Data-driven seasonal pattern identification
#     # Compute monthly average temperature across all years
#     monthly_avg_temp = ele_data.groupby('month')['Temp_C'].mean().reset_index()
    
#     # Use KMeans to cluster months into 4 seasons based on avg temp
#     scaler = StandardScaler()
#     monthly_temp_scaled = scaler.fit_transform(monthly_avg_temp[['Temp_C']])
#     kmeans_seasons = KMeans(n_clusters=4, random_state=42, n_init=10)
#     monthly_avg_temp['season_cluster'] = kmeans_seasons.fit_predict(monthly_temp_scaled)
    
#     # Assign season labels based on clusters (sorted by avg temp)
#     # Sort clusters by mean temp for logical labeling
#     cluster_means = monthly_avg_temp.groupby('season_cluster')['Temp_C'].mean().sort_values()
#     sorted_clusters = cluster_means.index.tolist()
#     season_mapping = {}
#     for i, cluster in enumerate(sorted_clusters):
#         if i == 0:
#             season_mapping[cluster] = 'Cold Dry'
#         elif i == 1:
#             season_mapping[cluster] = 'Semi-Cold Dry'
#         elif i == 2:
#             season_mapping[cluster] = 'Warm Semi-Wet'
#         else:
#             season_mapping[cluster] = 'Hot Wet'
    
#     monthly_avg_temp['season'] = monthly_avg_temp['season_cluster'].map(season_mapping)
#     month_to_season = dict(zip(monthly_avg_temp['month'], monthly_avg_temp['season']))
    
#     # Add season to ele_data
#     ele_data['season'] = ele_data['month'].map(month_to_season)
    
#     print("Identified seasonal patterns:", month_to_season)
    
#     # Process for each elephant and each year separately
#     for ind in individuals:
#         ind_data = ele_data[ele_data['elephant_id'] == ind].copy()
#         unique_years = sorted(ind_data['year'].unique())
        
#         for year in unique_years:
#             year_data = ind_data[ind_data['year'] == year].copy()
#             if len(year_data) == 0:
#                 continue
            
#             year_data['waterhole_cat'] = pd.Categorical(year_data['waterhole'])
            
#             # Prepare for clustering: features - hour, Temp_C, waterhole (one-hot)
#             features = ['hour', 'Temp_C']
#             categorical_features = ['waterhole']
#             preprocessor = ColumnTransformer(
#                 transformers=[
#                     ('num', StandardScaler(), features),
#                     ('cat', OneHotEncoder(), categorical_features)
#                 ])
            
#             X = preprocessor.fit_transform(year_data[features + categorical_features])
            
#             # KMeans Clustering with 5 clusters (adjustable)
#             kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
#             year_data['cluster'] = kmeans.fit_predict(X)
            
#             # Group by cluster to find start/end times (min/max DateTime per cluster)
#             clustered_data = year_data[['elephant_id', 'Longitude', 'Latitude', 'DateTime', 'date', 'year', 'hour', 'waterhole', 'Temp_C', 'cluster', 'season']].copy()
#             clustered_data['time'] = clustered_data['DateTime'].dt.time
#             clustered_data['start_time'] = clustered_data.groupby(['cluster'])['DateTime'].transform('min')
#             clustered_data['end_time'] = clustered_data.groupby(['cluster'])['DateTime'].transform('max')
#             clustered_data['start_time_str'] = clustered_data['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
#             clustered_data['end_time_str'] = clustered_data['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
#             # Select columns for CSV (now including season)
#             output_cols = ['elephant_id', 'Longitude', 'Latitude', 'time', 'date', 'year', 'cluster', 'start_time_str', 'end_time_str', 'hour', 'waterhole', 'Temp_C', 'season']
#             clustered_data = clustered_data[output_cols]
            
#             # Save separate CSV for this elephant-year
#             csv_filename = f'{ind}_{year}_clusters_kmeans_with_seasons.csv'
#             csv_path = os.path.join(plots_dir, csv_filename)
#             clustered_data.to_csv(csv_path, index=False)
#             print(f"Saved CSV for {ind} - {year}: {csv_path}")
    
#     print("All individual elephant-year CSV files saved to:", plots_dir)


# KMeans Clustering with individual elephant-year CSV outputs and seasonal patterns

# import pandas as pd
# import glob
# import numpy as np
# import os
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
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

# # Define paths (adjust if needed for exact file structure)
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')
# plots_dir = os.path.join(save_path, 'analysis', 'plots2')

# # Create plots directory if it doesn't exist
# os.makedirs(plots_dir, exist_ok=True)

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
# else:
#     # Also add encoding to elephant files if needed
#     ele_data_list = []
#     for f in elephant_files:
#         try:
#             df = pd.read_csv(f, encoding='utf-8')
#         except UnicodeDecodeError:
#             df = pd.read_csv(f, encoding='latin-1')
        
#         # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
#         filename = os.path.basename(f).replace('.csv', '')
#         elephant_id = filename.split('_')[0]
#         df['elephant_id'] = elephant_id  # Add as column
        
#         ele_data_list.append(df)
    
#     ele_data = pd.concat(ele_data_list, ignore_index=True)
    
#     # Clean column names
#     ele_data.columns = ele_data.columns.str.strip()
    
#     # If 'individual-local-identifier' exists, but use 'elephant_id' instead
#     # Drop 'individual-local-identifier' if present, use elephant_id
#     if 'individual-local-identifier' in ele_data.columns:
#         ele_data = ele_data.drop(columns=['individual-local-identifier'])
    
#     # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
#     # Handle possible column name variations
#     time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
#     ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
    
#     # Extract year, month, and fractional hour for plotting
#     ele_data['year'] = ele_data['DateTime'].dt.year
#     ele_data['month'] = ele_data['DateTime'].dt.month
#     ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
#     ele_data['date'] = ele_data['DateTime'].dt.date
    
#     # Load and integrate weather data (now including Precip_mm)
#     try:
#         weather = pd.read_csv(weather_path, encoding='utf-8')
#     except UnicodeDecodeError:
#         weather = pd.read_csv(weather_path, encoding='latin-1')
    
#     # Assume columns 'Date' (YYYY-MM-DD), 'Temp_C', 'Precip_mm'
#     weather['date'] = pd.to_datetime(weather['Date']).dt.date
#     temp_dict = dict(zip(weather['date'], weather['Temp_C']))
#     precip_dict = dict(zip(weather['date'], weather['Precip_mm']))
#     ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
#     ele_data['Precip_mm'] = ele_data['date'].map(precip_dict)
    
#     # Define radius (variable - change as needed)
#     radius = 1.0  # km
    
#     # Vectorized waterhole assignment
#     print("Assigning waterholes to elephant observations (vectorized)...")
#     ele_lons = ele_data['Longitude'].values
#     ele_lats = ele_data['Latitude'].values
#     wh_lons = waterholes['lon'].values
#     wh_lats = waterholes['lat'].values
    
#     # Compute distance matrix
#     dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
    
#     # Find min dist and closest index for each elephant observation
#     min_dists = np.min(dist_matrix, axis=1)
#     closest_idxs = np.argmin(dist_matrix, axis=1)
    
#     # Assign waterhole if within radius
#     wh_names = waterholes['Name'].values
#     ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
    
#     # Drop rows with no assigned waterhole or missing Temp_C/Precip_mm
#     ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C', 'Precip_mm'])
    
#     # Get sorted unique waterhole names for x-axis
#     waterholes_list = sorted(waterholes['Name'].unique())
    
#     # Create categorical for waterholes and months
#     ele_data['wh_cat'] = pd.Categorical(ele_data['waterhole'], categories=waterholes_list)
#     ele_data['month_cat'] = pd.Categorical(ele_data['month'], categories=range(1,13))
    
#     # Get unique individuals (now using true elephant_id prefix)
#     individuals = sorted(ele_data['elephant_id'].unique())
    
#     print(f"Processing {len(individuals)} individuals...")
    
#     # Data-driven seasonal pattern identification (now using both Temp_C and Precip_mm)
#     # Compute monthly average temperature and precipitation across all years
#     monthly_avg = ele_data.groupby('month')[['Temp_C', 'Precip_mm']].mean().reset_index()
    
#     # Use KMeans to cluster months into 4 seasons based on avg temp and precip
#     scaler = StandardScaler()
#     monthly_scaled = scaler.fit_transform(monthly_avg[['Temp_C', 'Precip_mm']])
#     kmeans_seasons = KMeans(n_clusters=4, random_state=42, n_init=10)
#     monthly_avg['season_cluster'] = kmeans_seasons.fit_predict(monthly_scaled)
    
#     # Map month to season_cluster (numerical, no hardcoded labels)
#     month_to_season_cluster = dict(zip(monthly_avg['month'], monthly_avg['season_cluster']))
    
#     # Add season_cluster to ele_data
#     ele_data['season_cluster'] = ele_data['month'].map(month_to_season_cluster)
    
#     print("Identified seasonal clusters (numerical):", month_to_season_cluster)
#     print("Monthly avg temp and precip:", monthly_avg[['month', 'Temp_C', 'Precip_mm', 'season_cluster']].to_string(index=False))
    
#     # Process for each elephant and each year separately
#     for ind in individuals:
#         ind_data = ele_data[ele_data['elephant_id'] == ind].copy()
#         unique_years = sorted(ind_data['year'].unique())
        
#         for year in unique_years:
#             year_data = ind_data[ind_data['year'] == year].copy()
#             if len(year_data) == 0:
#                 continue
            
#             year_data['waterhole_cat'] = pd.Categorical(year_data['waterhole'])
            
#             # Prepare for clustering: features - hour, Temp_C, Precip_mm, waterhole (one-hot)
#             features = ['hour', 'Temp_C', 'Precip_mm']
#             categorical_features = ['waterhole']
#             preprocessor = ColumnTransformer(
#                 transformers=[
#                     ('num', StandardScaler(), features),
#                     ('cat', OneHotEncoder(), categorical_features)
#                 ])
            
#             X = preprocessor.fit_transform(year_data[features + categorical_features])
            
#             # KMeans Clustering with 5 clusters (adjustable)
#             kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
#             year_data['cluster'] = kmeans.fit_predict(X)
            
#             # Group by cluster to find start/end times (min/max DateTime per cluster)
#             clustered_data = year_data[['elephant_id', 'Longitude', 'Latitude', 'DateTime', 'date', 'year', 'hour', 'waterhole', 'Temp_C', 'Precip_mm', 'cluster', 'season_cluster']].copy()
#             clustered_data['time'] = clustered_data['DateTime'].dt.time
#             clustered_data['start_time'] = clustered_data.groupby(['cluster'])['DateTime'].transform('min')
#             clustered_data['end_time'] = clustered_data.groupby(['cluster'])['DateTime'].transform('max')
#             clustered_data['start_time_str'] = clustered_data['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
#             clustered_data['end_time_str'] = clustered_data['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
#             # Select columns for CSV (now including Precip_mm and season_cluster)
#             output_cols = ['elephant_id', 'Longitude', 'Latitude', 'time', 'date', 'year', 'cluster', 'start_time_str', 'end_time_str', 'hour', 'waterhole', 'Temp_C', 'Precip_mm', 'season_cluster']
#             clustered_data = clustered_data[output_cols]
            
#             # Save separate CSV for this elephant-year
#             csv_filename = f'{ind}_{year}_clusters_kmeans_with_precip_seasons.csv'
#             csv_path = os.path.join(plots_dir, csv_filename)
#             clustered_data.to_csv(csv_path, index=False)
#             print(f"Saved CSV for {ind} - {year}: {csv_path}")
    
#     print("All individual elephant-year CSV files saved to:", plots_dir)

# Spectral Clustering with all years combined CSV output and seasonal patterns

import pandas as pd
import glob
import numpy as np
import os
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

def haversine_vectorized(lon1, lat1, lon2, lat2):
    """
    Vectorized haversine distance calculation.
    """
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)
    dlon = lon2 - lon1[:, np.newaxis]
    dlat = lat2 - lat1[:, np.newaxis]
    a = (np.sin(dlat / 2)**2 + 
         np.cos(lat1[:, np.newaxis]) * np.cos(lat2[np.newaxis, :]) * 
         np.sin(dlon / 2)**2)
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

# Define paths (adjust if needed for exact file structure)
base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_Data_Analysis'
fe_path = os.path.join(base_path, 'fe')
me_path = os.path.join(base_path, 'me')
waterholes_path = os.path.join(base_path, 'Waterholes.csv')
weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')
plots_dir = os.path.join(save_path, 'analysis', 'plots3')

# Create plots directory if it doesn't exist
os.makedirs(plots_dir, exist_ok=True)

# Load waterholes data with encoding fix
waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
waterholes['lat'] = waterholes['Latitude']
waterholes['lon'] = waterholes['Longitude']

# Load elephant data from all CSV files in fe and me folders, assigning filename prefix as elephant ID
elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
if not elephant_files:
    print("No CSV files found in fe or me directories.")
else:
    # Also add encoding to elephant files if needed
    ele_data_list = []
    for f in elephant_files:
        try:
            df = pd.read_csv(f, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(f, encoding='latin-1')
        
        # Extract elephant ID from filename prefix (e.g., '01fe_cold_dry_2009.csv' -> '01fe')
        filename = os.path.basename(f).replace('.csv', '')
        elephant_id = filename.split('_')[0]
        df['elephant_id'] = elephant_id  # Add as column
        
        ele_data_list.append(df)
    
    ele_data = pd.concat(ele_data_list, ignore_index=True)
    
    # Clean column names
    ele_data.columns = ele_data.columns.str.strip()
    
    # If 'individual-local-identifier' exists, but use 'elephant_id' instead
    # Drop 'individual-local-identifier' if present, use elephant_id
    if 'individual-local-identifier' in ele_data.columns:
        ele_data = ele_data.drop(columns=['individual-local-identifier'])
    
    # Parse DateTime (assuming 'Date' is 'YYYY-MM-DD' and 'timeAPM' or 'Time' is 'HH:MM:SS')
    # Handle possible column name variations
    time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
    ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
    
    # Extract year, month, and fractional hour for plotting
    ele_data['year'] = ele_data['DateTime'].dt.year
    ele_data['month'] = ele_data['DateTime'].dt.month
    ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
    ele_data['date'] = ele_data['DateTime'].dt.date
    
    # Load and integrate weather data (now including Precip_mm)
    try:
        weather = pd.read_csv(weather_path, encoding='utf-8')
    except UnicodeDecodeError:
        weather = pd.read_csv(weather_path, encoding='latin-1')
    
    # Assume columns 'Date' (YYYY-MM-DD), 'Temp_C', 'Precip_mm'
    weather['date'] = pd.to_datetime(weather['Date']).dt.date
    temp_dict = dict(zip(weather['date'], weather['Temp_C']))
    precip_dict = dict(zip(weather['date'], weather['Precip_mm']))
    ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
    ele_data['Precip_mm'] = ele_data['date'].map(precip_dict)
    
    # Define radius (variable - change as needed)
    radius = 1.0  # km
    
    # Vectorized waterhole assignment
    print("Assigning waterholes to elephant observations (vectorized)...")
    ele_lons = ele_data['Longitude'].values
    ele_lats = ele_data['Latitude'].values
    wh_lons = waterholes['lon'].values
    wh_lats = waterholes['lat'].values
    
    # Compute distance matrix
    dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
    
    # Find min dist and closest index for each elephant observation
    min_dists = np.min(dist_matrix, axis=1)
    closest_idxs = np.argmin(dist_matrix, axis=1)
    
    # Assign waterhole if within radius
    wh_names = waterholes['Name'].values
    ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
    
    # Drop rows with no assigned waterhole or missing Temp_C/Precip_mm
    ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C', 'Precip_mm'])
    
    # Get sorted unique waterhole names for x-axis
    waterholes_list = sorted(waterholes['Name'].unique())
    
    # Create categorical for waterholes and months
    ele_data['wh_cat'] = pd.Categorical(ele_data['waterhole'], categories=waterholes_list)
    ele_data['month_cat'] = pd.Categorical(ele_data['month'], categories=range(1,13))
    
    # Get unique individuals (now using true elephant_id prefix)
    individuals = sorted(ele_data['elephant_id'].unique())
    
    print(f"Processing {len(individuals)} individuals...")
    
    # Data-driven seasonal pattern identification (now using both Temp_C and Precip_mm)
    # Compute monthly average temperature and precipitation across all years
    monthly_avg = ele_data.groupby('month')[['Temp_C', 'Precip_mm']].mean().reset_index()
    
    # Use KMeans to cluster months into 4 seasons based on avg temp and precip
    scaler = StandardScaler()
    monthly_scaled = scaler.fit_transform(monthly_avg[['Temp_C', 'Precip_mm']])
    kmeans_seasons = KMeans(n_clusters=4, random_state=42, n_init=10)
    monthly_avg['season_cluster'] = kmeans_seasons.fit_predict(monthly_scaled)
    
    # Map month to season_cluster (numerical, no hardcoded labels)
    month_to_season_cluster = dict(zip(monthly_avg['month'], monthly_avg['season_cluster']))
    
    # Add season_cluster to ele_data
    ele_data['season_cluster'] = ele_data['month'].map(month_to_season_cluster)
    
    print("Identified seasonal clusters (numerical):", month_to_season_cluster)
    print("Monthly avg temp and precip:", monthly_avg[['month', 'Temp_C', 'Precip_mm', 'season_cluster']].to_string(index=False))
    
    # Process for each elephant and each year separately, for both KMeans and SpectralClustering
    for ind in individuals:
        ind_data = ele_data[ele_data['elephant_id'] == ind].copy()
        unique_years = sorted(ind_data['year'].unique())
        
        for year in unique_years:
            year_data = ind_data[ind_data['year'] == year].copy()
            if len(year_data) == 0:
                continue
            
            year_data['waterhole_cat'] = pd.Categorical(year_data['waterhole'])
            
            # Prepare for clustering: features - hour, Temp_C, Precip_mm, waterhole (one-hot)
            features = ['hour', 'Temp_C', 'Precip_mm']
            categorical_features = ['waterhole']
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', StandardScaler(), features),
                    ('cat', OneHotEncoder(), categorical_features)
                ])
            
            X = preprocessor.fit_transform(year_data[features + categorical_features])
            
            # KMeans Clustering with 5 clusters
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            year_data_kmeans = year_data.copy()
            year_data_kmeans['cluster'] = kmeans.fit_predict(X)
            
            # Group by cluster for KMeans
            clustered_kmeans = year_data_kmeans[['elephant_id', 'Longitude', 'Latitude', 'DateTime', 'date', 'year', 'hour', 'waterhole', 'Temp_C', 'Precip_mm', 'cluster', 'season_cluster']].copy()
            clustered_kmeans['time'] = clustered_kmeans['DateTime'].dt.time
            clustered_kmeans['start_time'] = clustered_kmeans.groupby(['cluster'])['DateTime'].transform('min')
            clustered_kmeans['end_time'] = clustered_kmeans.groupby(['cluster'])['DateTime'].transform('max')
            clustered_kmeans['start_time_str'] = clustered_kmeans['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            clustered_kmeans['end_time_str'] = clustered_kmeans['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Select columns for KMeans CSV
            output_cols = ['elephant_id', 'Longitude', 'Latitude', 'time', 'date', 'year', 'cluster', 'start_time_str', 'end_time_str', 'hour', 'waterhole', 'Temp_C', 'Precip_mm', 'season_cluster']
            clustered_kmeans = clustered_kmeans[output_cols]
            
            # Save KMeans CSV
            kmeans_filename = f'{ind}_{year}_kmeans_clusters_with_precip_seasons.csv'
            kmeans_path = os.path.join(plots_dir, kmeans_filename)
            clustered_kmeans.to_csv(kmeans_path, index=False)
            print(f"Saved KMeans CSV for {ind} - {year}: {kmeans_path}")
            
            # Spectral Clustering with 5 clusters
            spectral = SpectralClustering(n_clusters=5, random_state=42, affinity='rbf')
            year_data_spectral = year_data.copy()
            year_data_spectral['cluster'] = spectral.fit_predict(X)
            
            # Group by cluster for Spectral
            clustered_spectral = year_data_spectral[['elephant_id', 'Longitude', 'Latitude', 'DateTime', 'date', 'year', 'hour', 'waterhole', 'Temp_C', 'Precip_mm', 'cluster', 'season_cluster']].copy()
            clustered_spectral['time'] = clustered_spectral['DateTime'].dt.time
            clustered_spectral['start_time'] = clustered_spectral.groupby(['cluster'])['DateTime'].transform('min')
            clustered_spectral['end_time'] = clustered_spectral.groupby(['cluster'])['DateTime'].transform('max')
            clustered_spectral['start_time_str'] = clustered_spectral['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            clustered_spectral['end_time_str'] = clustered_spectral['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Select columns for Spectral CSV
            clustered_spectral = clustered_spectral[output_cols]
            
            # Save Spectral CSV
            spectral_filename = f'{ind}_{year}_spectral_clusters_with_precip_seasons.csv'
            spectral_path = os.path.join(plots_dir, spectral_filename)
            clustered_spectral.to_csv(spectral_path, index=False)
            print(f"Saved Spectral CSV for {ind} - {year}: {spectral_path}")
    
    print("All individual elephant-year CSV files (KMeans and Spectral) saved to:", plots_dir)