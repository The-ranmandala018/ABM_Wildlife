# import pandas as pd
# import os
# from datetime import datetime
# import folium

# # Input and output directories (absolute paths as provided)
# input_base_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data"
# output_base_dir = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Filter_By_Month"

# # Ensure output base directory exists
# os.makedirs(output_base_dir, exist_ok=True)

# # Subfolders to process (e.g., 'fe', 'me')
# subfolders = ['fe', 'me']  # Add more if needed

# # Define 12 distinct colors for months (1-12)
# month_colors = [
#     '#FF0000',  # Jan: Red
#     '#00FF00',  # Feb: Green
#     '#0000FF',  # Mar: Blue
#     '#FFFF00',  # Apr: Yellow
#     '#FF00FF',  # May: Magenta
#     '#00FFFF',  # Jun: Cyan
#     '#FFA500',  # Jul: Orange
#     '#800080',  # Aug: Purple
#     '#FFC0CB',  # Sep: Pink
#     '#90EE90',  # Oct: Light Green
#     '#FFB6C1',  # Nov: Light Pink
#     '#DDA0DD'   # Dec: Plum
# ]

# for subfolder in subfolders:
#     input_subdir = os.path.join(input_base_dir, subfolder)
#     output_subdir = os.path.join(output_base_dir, subfolder)
    
#     # Ensure output subdir exists
#     os.makedirs(output_subdir, exist_ok=True)
    
#     if not os.path.exists(input_subdir):
#         print(f"Subfolder {input_subdir} does not exist. Skipping.")
#         continue
    
#     # Find all CSV files in the subfolder
#     csv_files = [f for f in os.listdir(input_subdir) if f.endswith('.csv')]
    
#     for csv_file in csv_files:
#         file_path = os.path.join(input_subdir, csv_file)
#         print(f"Processing {file_path}...")
        
#         # Load the CSV
#         df = pd.read_csv(file_path)
        
#         # Create DateTime column (assuming 'Date' and 'Time' columns exist)
#         df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        
#         # Add Month column for plotting (1-12)
#         df['Month'] = df['DateTime'].dt.month
        
#         # Group by month-year period and save each month's data
#         periods = df['DateTime'].dt.to_period('M').unique()
#         for p in sorted(periods):
#             df_month = df[df['DateTime'].dt.to_period('M') == p].copy()
            
#             if not df_month.empty:
#                 # Extract base name without .csv
#                 base_name = csv_file.replace('.csv', '')
#                 output_filename = f"{base_name}_{p}.csv"
#                 output_file = os.path.join(output_subdir, output_filename)
#                 df_month.to_csv(output_file, index=False)
#                 print(f"Saved month {p} data to {output_file} ({len(df_month)} rows).")
        
#         # Plotting: One map with all data, colored by month (without filtering)
#         if not df.empty and 'Lat' in df.columns and 'Lon' in df.columns:  # TODO: Replace 'Lat'/'Lon' with actual column names once known
#             # Calculate center for the map
#             center_lat = df['Lat'].mean()
#             center_lon = df['Lon'].mean()
            
#             # Create folium map for all months with colors
#             all_months_map = folium.Map(location=[center_lat, center_lon], zoom_start=10)
            
#             # Add points colored by month
#             for idx, row in df.iterrows():
#                 if pd.notna(row['Lat']) and pd.notna(row['Lon']):
#                     color = month_colors[row['Month'] - 1]
#                     folium.CircleMarker(
#                         location=[row['Lat'], row['Lon']],
#                         radius=3,
#                         popup=f"Date: {row['Date']}, Time: {row['Time']}, Month: {row['Month']}",
#                         color=color,
#                         fill=True,
#                         fillColor=color,
#                         fillOpacity=0.7
#                     ).add_to(all_months_map)
            
#             # Save the all-months colored map
#             all_months_output = os.path.join(output_subdir, f"{base_name}_All_Months_Colored_Map.html")
#             all_months_map.save(all_months_output)
#             print(f"Saved all-months colored map to {all_months_output}.")
            
#             # Create separate maps for each of the 12 months (even if empty, but skip empty)
#             for month in range(1, 13):
#                 df_month_plot = df[df['Month'] == month].copy()
#                 if not df_month_plot.empty:
#                     # Calculate center for this month
#                     month_center_lat = df_month_plot['Lat'].mean()
#                     month_center_lon = df_month_plot['Lon'].mean()
                    
#                     # Create folium map for this month
#                     month_map = folium.Map(location=[month_center_lat, month_center_lon], zoom_start=10)
                    
#                     # Add points for this month (all same color)
#                     color = month_colors[month - 1]
#                     for idx, row in df_month_plot.iterrows():
#                         if pd.notna(row['Lat']) and pd.notna(row['Lon']):
#                             folium.CircleMarker(
#                                 location=[row['Lat'], row['Lon']],
#                                 radius=3,
#                                 popup=f"Date: {row['Date']}, Time: {row['Time']}",
#                                 color=color,
#                                 fill=True,
#                                 fillColor=color,
#                                 fillOpacity=0.7
#                             ).add_to(month_map)
                    
#                     # Save the monthly map
#                     month_output = os.path.join(output_subdir, f"{base_name}_Month{month}_Map.html")
#                     month_map.save(month_output)
#                     print(f"Saved Month {month} map to {month_output} ({len(df_month_plot)} rows).")
#                 else:
#                     print(f"No data for Month {month} in {csv_file}.")
#         else:
#             print(f"Skipping plotting for {csv_file}: Missing 'Lat'/'Lon' columns or empty data.")
#             print(f"Available columns: {df.columns.tolist()}")  # This will show you the real column names!
        
#         print(f"Finished processing {csv_file}.")

# print("All files processed.")

# import pandas as pd
# import os
# import folium
# from collections import defaultdict

# # Some color schemes for months
# month_colors = {
#     1: '#008000',   # January: Green
#     2: '#FF0000',   # February: Red
#     3: '#0000FF',   # March: Blue
#     4: '#800080',   # April: Purple
#     5: '#FFA500',   # May: Orange
#     6: '#00FFFF',   # June: Cyan
#     7: '#FFFF00',   # July: Yellow
#     8: '#FF00FF',   # August: Magenta
#     9: '#A52A2A',   # September: Brown
#     10: '#808080',  # October: Gray
#     11: '#000080',  # November: Navy
#     12: '#FFC0CB'   # December: Pink
# }

# # Month names for labels
# month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# in_f = "../Filter_By_Month"

# # Dictionary to group files by base name (e.g., all months for one entity/year)
# grouped_files = defaultdict(list)

# for occ in os.listdir(in_f):
#     folderpath = f"{in_f}/{occ}"
#     if not os.path.exists(folderpath):
#         continue
    
#     all_csvs = [f for f in os.listdir(folderpath) if f.endswith('.csv')]
    
#     for fname in all_csvs:
#         # Parse base name: e.g., "06me_hot_wet_2009_2009-02.csv" -> base="06me_hot_wet_2009", month=2
#         parts = fname.rsplit('_', 2)
#         if len(parts) == 3 and parts[-1].endswith('.csv'):
#             period_str = parts[-1].replace('.csv', '')
#             base_parts = parts[:-1]
#             base = '_'.join(base_parts)
#             try:
#                 month_num = int(period_str.split('-')[-1])
#                 if 1 <= month_num <= 12:
#                     grouped_files[(occ, base)].append((fname, month_num))
#             except ValueError:
#                 pass  # Skip if not parseable

# for (occ, base), file_list in grouped_files.items():
#     print(f"\nProcessing base '{base}' in '{occ}' with {len(file_list)} monthly files...")
    
#     # Load data for all months
#     all_month_data = {}
#     for fname, month_num in sorted(file_list, key=lambda x: x[1]):
#         filepath = f"{in_f}/{occ}/{fname}"
#         df_month = pd.read_csv(filepath)
        
#         print(f"  Loading {fname}...")
#         print(f"    Shape before dropna: {df_month.shape}")
        
#         # Remove NaNs
#         df_month.dropna(inplace=True)
#         print(f"    Shape after dropna: {df_month.shape}")
        
#         if df_month.empty:
#             print(f"    Skipping empty {fname}")
#             continue
        
#         # Create DateTime and Month (use filename month as primary)
#         df_month['DateTime'] = pd.to_datetime(df_month['Date'] + ' ' + df_month['Time'])
#         df_month['Month'] = month_num  # Override with filename month for consistency
        
#         all_month_data[month_num] = df_month
    
#     if not all_month_data:
#         print(f"No valid data for base '{base}' in '{occ}'.")
#         continue
    
#     print(f"Loaded data for {len(all_month_data)} months in '{base}'.")
    
#     # Check columns (assume consistent across months)
#     sample_df = list(all_month_data.values())[0]
#     if 'Latitude' not in sample_df.columns or 'Longitude' not in sample_df.columns:
#         print(f"Skipping '{base}': Missing 'Latitude' or 'Longitude' columns.")
#         print(f"Available columns: {sample_df.columns.tolist()}")
#         continue
    
#     # Map output paths
#     parentpath_map = f"../maps_months/{occ}"
#     base_folder = os.path.join(parentpath_map, base)
#     if not os.path.exists(base_folder):
#         os.makedirs(base_folder)
    
#     # Generate individual monthly maps and collect their paths
#     monthly_maps = {}
#     for month in range(1, 13):
#         if month in all_month_data:
#             month_df = all_month_data[month]
#             if not month_df.empty:
#                 # Calculate center
#                 center_lat = month_df['Latitude'].mean()
#                 center_lon = month_df['Longitude'].mean()
#                 print(f"  Month {month} center: [{center_lat:.4f}, {center_lon:.4f}]")
                
#                 # Create Folium map for this month
#                 m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles='OpenStreetMap')
                
#                 color = month_colors[month]
#                 num_points = 0
#                 for _, row in month_df.iterrows():
#                     if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
#                         folium.CircleMarker(
#                             location=[row['Latitude'], row['Longitude']],
#                             radius=5,
#                             color=color,
#                             fill=True,
#                             fill_color=color,
#                             popup=f"DateTime: {row['DateTime']}, Month: {month}"
#                         ).add_to(m)
#                         num_points += 1
                
#                 if num_points > 0:
#                     map_filename = f"{base}_Month{month_names[month-1]}_Map.html"
#                     map_path = os.path.join(base_folder, map_filename)
#                     m.save(map_path)
#                     monthly_maps[month] = map_filename
#                     print(f"  Saved Month {month} map: {map_filename} ({num_points} points)")
#                 else:
#                     print(f"  Month {month}: No valid points.")
#             else:
#                 print(f"  Month {month}: Empty after processing.")
#         else:
#             print(f"  No file for Month {month}.")
    
#     # Create main grid HTML with embedded iframes for the 12 maps (3x4 grid)
#     if monthly_maps:
#         grid_html = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>{base} - 12 Months Cartesian Map Grid</title>
#             <style>
#                 body {{ font-family: Arial, sans-serif; margin: 20px; }}
#                 h1 {{ text-align: center; }}
#                 .grid-container {{
#                     display: grid;
#                     grid-template-columns: repeat(4, 1fr);  /* 4 columns */
#                     grid-gap: 10px;
#                     max-width: 1400px;
#                     margin: 0 auto;
#                 }}
#                 .map-box {{
#                     border: 1px solid #ccc;
#                     padding: 10px;
#                     text-align: center;
#                 }}
#                 .map-box h3 {{ margin: 0 0 10px 0; }}
#                 iframe {{
#                     width: 100%;
#                     height: 250px;
#                     border: none;
#                 }}
#                 .missing {{ background-color: #f0f0f0; padding: 100px; text-align: center; color: #999; }}
#             </style>
#         </head>
#         <body>
#             <h1>{base} - Monthly Maps (Cartesian Grid View)</h1>
#             <div class="grid-container">
#         """
        
#         for month in range(1, 13):
#             month_name = month_names[month-1]
#             if month in monthly_maps:
#                 map_file = monthly_maps[month]
#                 grid_html += f"""
#                 <div class="map-box">
#                     <h3>{month_name}</h3>
#                     <iframe src="{map_file}"></iframe>
#                 </div>
#                 """
#             else:
#                 grid_html += f"""
#                 <div class="map-box missing">
#                     <h3>{month_name}</h3>
#                     <p>No data available</p>
#                 </div>
#                 """
        
#         grid_html += """
#             </div>
#         </body>
#         </html>
#         """
        
#         # Save the grid HTML
#         grid_filename = f"{base}_12_Months_Grid.html"
#         grid_path = os.path.join(base_folder, grid_filename)
#         with open(grid_path, 'w') as f:
#             f.write(grid_html)
#         print(f"Saved Cartesian grid HTML to {grid_path}")

# print("All monthly maps and grid views processed.")

# import pandas as pd
# import os
# import folium
# from collections import defaultdict

# # Some color schemes for months
# month_colors = {
#     1: '#008000',   # January: Green
#     2: '#FF0000',   # February: Red
#     3: '#0000FF',   # March: Blue
#     4: '#800080',   # April: Purple
#     5: '#FFA500',   # May: Orange
#     6: '#00FFFF',   # June: Cyan
#     7: '#FFFF00',   # July: Yellow
#     8: '#FF00FF',   # August: Magenta
#     9: '#A52A2A',   # September: Brown
#     10: '#808080',  # October: Gray
#     11: '#000080',  # November: Navy
#     12: '#FFC0CB'   # December: Pink
# }

# # Month names for labels
# month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# # Season definitions (DJF, MAM, JJA, SON)
# seasons = {
#     'Winter': [12, 1, 2],
#     'Spring': [3, 4, 5],
#     'Summer': [6, 7, 8],
#     'Fall': [9, 10, 11]
# }

# # Color schemes for seasons
# season_colors = {
#     'Winter': '#4169E1',  # Royal blue
#     'Spring': '#228B22',  # Forest green
#     'Summer': '#FF4500',  # Orange red
#     'Fall': '#DAA520'     # Golden rod
# }

# season_names = ['Winter', 'Spring', 'Summer', 'Fall']

# in_f = "../Filter_By_Month"

# # Dictionary to group files by base name (e.g., all months for one entity/year)
# grouped_files = defaultdict(list)

# for occ in os.listdir(in_f):
#     folderpath = f"{in_f}/{occ}"
#     if not os.path.exists(folderpath):
#         continue
    
#     all_csvs = [f for f in os.listdir(folderpath) if f.endswith('.csv')]
    
#     for fname in all_csvs:
#         # Parse base name: e.g., "06me_hot_wet_2009_2009-02.csv" -> base="06me_hot_wet_2009", month=2
#         parts = fname.rsplit('_', 2)
#         if len(parts) == 3 and parts[-1].endswith('.csv'):
#             period_str = parts[-1].replace('.csv', '')
#             base_parts = parts[:-1]
#             base = '_'.join(base_parts)
#             try:
#                 month_num = int(period_str.split('-')[-1])
#                 if 1 <= month_num <= 12:
#                     grouped_files[(occ, base)].append((fname, month_num))
#             except ValueError:
#                 pass  # Skip if not parseable

# for (occ, base), file_list in grouped_files.items():
#     print(f"\nProcessing base '{base}' in '{occ}' with {len(file_list)} monthly files...")
    
#     # Load data for all months
#     all_month_data = {}
#     for fname, month_num in sorted(file_list, key=lambda x: x[1]):
#         filepath = f"{in_f}/{occ}/{fname}"
#         df_month = pd.read_csv(filepath)
        
#         print(f"  Loading {fname}...")
#         print(f"    Shape before dropna: {df_month.shape}")
        
#         # Remove NaNs
#         df_month.dropna(inplace=True)
#         print(f"    Shape after dropna: {df_month.shape}")
        
#         if df_month.empty:
#             print(f"    Skipping empty {fname}")
#             continue
        
#         # Create DateTime and Month (use filename month as primary)
#         df_month['DateTime'] = pd.to_datetime(df_month['Date'] + ' ' + df_month['Time'])
#         df_month['Month'] = month_num  # Override with filename month for consistency
        
#         all_month_data[month_num] = df_month
    
#     if not all_month_data:
#         print(f"No valid data for base '{base}' in '{occ}'.")
#         continue
    
#     print(f"Loaded data for {len(all_month_data)} months in '{base}'.")
    
#     # Check columns (assume consistent across months)
#     sample_df = list(all_month_data.values())[0]
#     if 'Latitude' not in sample_df.columns or 'Longitude' not in sample_df.columns:
#         print(f"Skipping '{base}': Missing 'Latitude' or 'Longitude' columns.")
#         print(f"Available columns: {sample_df.columns.tolist()}")
#         continue
    
#     # Map output paths
#     parentpath_map = f"../maps_months/{occ}"
#     base_folder = os.path.join(parentpath_map, base)
#     if not os.path.exists(base_folder):
#         os.makedirs(base_folder)
    
#     # Generate individual monthly maps and collect their paths
#     monthly_maps = {}
#     for month in range(1, 13):
#         if month in all_month_data:
#             month_df = all_month_data[month]
#             if not month_df.empty:
#                 # Calculate center
#                 center_lat = month_df['Latitude'].mean()
#                 center_lon = month_df['Longitude'].mean()
#                 print(f"  Month {month} center: [{center_lat:.4f}, {center_lon:.4f}]")
                
#                 # Create Folium map for this month
#                 m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles='OpenStreetMap')
                
#                 color = month_colors[month]
#                 num_points = 0
#                 for _, row in month_df.iterrows():
#                     if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
#                         folium.CircleMarker(
#                             location=[row['Latitude'], row['Longitude']],
#                             radius=5,
#                             color=color,
#                             fill=True,
#                             fill_color=color,
#                             popup=f"DateTime: {row['DateTime']}, Month: {month}"
#                         ).add_to(m)
#                         num_points += 1
                
#                 if num_points > 0:
#                     map_filename = f"{base}_Month{month_names[month-1]}_Map.html"
#                     map_path = os.path.join(base_folder, map_filename)
#                     m.save(map_path)
#                     monthly_maps[month] = map_filename
#                     print(f"  Saved Month {month} map: {map_filename} ({num_points} points)")
#                 else:
#                     print(f"  Month {month}: No valid points.")
#             else:
#                 print(f"  Month {month}: Empty after processing.")
#         else:
#             print(f"  No file for Month {month}.")
    
#     # Generate seasonal maps
#     seasonal_maps = {}
#     for season_name, months in seasons.items():
#         season_dfs = [all_month_data[m] for m in months if m in all_month_data]
#         if season_dfs:
#             season_df = pd.concat(season_dfs, ignore_index=True)
#             season_df.dropna(subset=['Latitude', 'Longitude'], inplace=True)
#             if not season_df.empty:
#                 center_lat = season_df['Latitude'].mean()
#                 center_lon = season_df['Longitude'].mean()
#                 print(f"  {season_name} center: [{center_lat:.4f}, {center_lon:.4f}]")
                
#                 m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles='OpenStreetMap')
                
#                 color = season_colors[season_name]
#                 num_points = 0
#                 for _, row in season_df.iterrows():
#                     folium.CircleMarker(
#                         location=[row['Latitude'], row['Longitude']],
#                         radius=5,
#                         color=color,
#                         fill=True,
#                         fill_color=color,
#                         popup=f"DateTime: {row['DateTime']}, Season: {season_name}"
#                     ).add_to(m)
#                     num_points += 1
                
#                 if num_points > 0:
#                     map_filename = f"{base}_{season_name}_Map.html"
#                     map_path = os.path.join(base_folder, map_filename)
#                     m.save(map_path)
#                     seasonal_maps[season_name] = map_filename
#                     print(f"  Saved {season_name} map: {map_filename} ({num_points} points)")
#                 else:
#                     print(f"  {season_name}: No valid points.")
#             else:
#                 print(f"  {season_name}: Empty after processing.")
#         else:
#             print(f"  No files for {season_name} months.")
    
#     # Create main grid HTML with embedded iframes for the 12 months + 4 seasons (4x4 grid)
#     if monthly_maps or seasonal_maps:
#         grid_html = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>{base} - Months and Seasons Cartesian Map Grid</title>
#             <style>
#                 body {{ font-family: Arial, sans-serif; margin: 20px; }}
#                 h1 {{ text-align: center; }}
#                 .grid-container {{
#                     display: grid;
#                     grid-template-columns: repeat(4, 1fr);  /* 4 columns */
#                     grid-gap: 10px;
#                     max-width: 1400px;
#                     margin: 0 auto;
#                 }}
#                 .map-box {{
#                     border: 1px solid #ccc;
#                     padding: 10px;
#                     text-align: center;
#                 }}
#                 .map-box h3 {{ margin: 0 0 10px 0; }}
#                 iframe {{
#                     width: 100%;
#                     height: 200px;
#                     border: none;
#                 }}
#                 .missing {{ background-color: #f0f0f0; padding: 80px; text-align: center; color: #999; }}
#             </style>
#         </head>
#         <body>
#             <h1>{base} - Monthly and Seasonal Maps (Cartesian Grid View)</h1>
#             <div class="grid-container">
#         """
        
#         # Add monthly maps
#         for month in range(1, 13):
#             month_name = month_names[month-1]
#             if month in monthly_maps:
#                 map_file = monthly_maps[month]
#                 grid_html += f"""
#                 <div class="map-box">
#                     <h3>{month_name}</h3>
#                     <iframe src="{map_file}"></iframe>
#                 </div>
#                 """
#             else:
#                 grid_html += f"""
#                 <div class="map-box missing">
#                     <h3>{month_name}</h3>
#                     <p>No data available</p>
#                 </div>
#                 """
        
#         # Add seasonal maps
#         for season_name in season_names:
#             if season_name in seasonal_maps:
#                 map_file = seasonal_maps[season_name]
#                 grid_html += f"""
#                 <div class="map-box">
#                     <h3>{season_name}</h3>
#                     <iframe src="{map_file}"></iframe>
#                 </div>
#                 """
#             else:
#                 grid_html += f"""
#                 <div class="map-box missing">
#                     <h3>{season_name}</h3>
#                     <p>No data available</p>
#                 </div>
#                 """
        
#         grid_html += """
#             </div>
#         </body>
#         </html>
#         """
        
#         # Save the grid HTML
#         grid_filename = f"{base}_Months_Seasons_Grid.html"
#         grid_path = os.path.join(base_folder, grid_filename)
#         with open(grid_path, 'w') as f:
#             f.write(grid_html)
#         print(f"Saved combined months and seasons grid HTML to {grid_path}")

# print("All monthly and seasonal maps and grid views processed.")



# import os
# import re
# import pandas as pd
# import folium
# from collections import defaultdict

# # ----------------------------------------------------------------------
# # 1. SETTINGS
# # ----------------------------------------------------------------------
# IN_FOLDER        = "../Filter_By_Month"          # <-- folder that contains occ sub‑folders
# OUT_ROOT         = "../maps_months"              # <-- where everything will be written
# ZOOM_START       = 9
# MAP_HEIGHT_PX    = 250

# MONTH_COLORS = {
#     1: '#008000', 2: '#FF0000', 3: '#0000FF', 4: '#800080',
#     5: '#FFA500', 6: '#00FFFF', 7: '#FFFF00', 8: '#FF00FF',
#     9: '#A52A2A',10: '#808080',11: '#000080',12: '#FFC0CB'
# }
# MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun',
#                'Jul','Aug','Sep','Oct','Nov','Dec']

# # ----------------------------------------------------------------------
# # 2. HELPER
# # ----------------------------------------------------------------------
# def ensure_folder(p):
#     if not os.path.isdir(p):
#         os.makedirs(p, exist_ok=True)
#         print(f"   Created folder: {p}")

# # ----------------------------------------------------------------------
# # 3. MAIN
# # ----------------------------------------------------------------------
# print(f"\n=== STARTING PROCESSING ===")
# print(f"Input folder : {os.path.abspath(IN_FOLDER)}")
# print(f"Output root  : {os.path.abspath(OUT_ROOT)}\n")

# if not os.path.isdir(IN_FOLDER):
#     raise SystemExit(f"ERROR: Input folder does not exist → {IN_FOLDER}")

# any_grid_created = False

# # ----------------------------------------------------------------------
# #   3.1  Walk every occ folder and collect *all* CSV files
# # ----------------------------------------------------------------------
# elephant_to_year_month = defaultdict(lambda: defaultdict(dict))   # elephant → year → month → df

# # regex to extract elephant ID (e.g. 01fe, 02me …)
# ELEPHANT_RE = re.compile(r'^(\d{2}[a-z]{2})')   # first two digits + two letters

# for occ in sorted(os.listdir(IN_FOLDER)):
#     occ_path = os.path.join(IN_FOLDER, occ)
#     if not os.path.isdir(occ_path):
#         print(f"   Skipping non‑folder: {occ}")
#         continue

#     print(f"\n--- OCCURRENCE FOLDER: {occ} ---")
#     csv_files = [f for f in os.listdir(occ_path) if f.lower().endswith('.csv')]
#     if not csv_files:
#         print(f"   No *.csv files in {occ_path}")
#         continue

#     for fname in csv_files:
#         print(f"   Examining file: {fname}")

#         # ---- 3.2  Extract elephant ID ---------------------------------
#         m_id = ELEPHANT_RE.search(fname)
#         if not m_id:
#             print(f"      → cannot extract elephant ID (need 01fe/02me … at start)")
#             continue
#         elephant_id = m_id.group(1).lower()
#         print(f"      → belongs to elephant '{elephant_id}'")

#         # ---- 3.3  Parse year‑month from the *last* two '_' parts -----
#         parts = fname.rsplit('_', 2)
#         if len(parts) != 3 or not parts[2].endswith('.csv'):
#             print(f"      → cannot parse (need 2 '_' before .csv)")
#             continue

#         period = parts[2].replace('.csv', '')
#         if '-' not in period:
#             print(f"      → period part has no '-'")
#             continue

#         try:
#             file_year  = int(period.split('-')[0])
#             file_month = int(period.split('-')[1])
#         except ValueError:
#             print(f"      → cannot convert year/month to int")
#             continue

#         if not (1 <= file_month <= 12):
#             print(f"      → month {file_month} out of range")
#             continue

#         # ---- 3.4  Load CSV -------------------------------------------
#         fp = os.path.join(occ_path, fname)
#         try:
#             df = pd.read_csv(fp)
#         except Exception as e:
#             print(f"      → FAILED to read CSV: {e}")
#             continue

#         print(f"      rows before dropna: {len(df)}")
#         df.dropna(subset=['Latitude', 'Longitude', 'Date', 'Time'], inplace=True)
#         print(f"      rows after  dropna: {len(df)}")
#         if df.empty:
#             print(f"      → empty after cleaning")
#             continue

#         # ---- 3.5  Add datetime column --------------------------------
#         df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
#         df['Month']    = file_month

#         # ---- 3.6  Store -----------------------------------------------
#         if file_month in elephant_to_year_month[elephant_id][file_year]:
#             elephant_to_year_month[elephant_id][file_year][file_month] = pd.concat(
#                 [elephant_to_year_month[elephant_id][file_year][file_month], df],
#                 ignore_index=True)
#         else:
#             elephant_to_year_month[elephant_id][file_year][file_month] = df

#         print(f"      → stored as elephant {elephant_id} | year {file_year} | month {file_month}")

# # ----------------------------------------------------------------------
# #   3.7  For every elephant → every year → build ONE 12‑month grid
# # ----------------------------------------------------------------------
# for elephant_id, year_dict in sorted(elephant_to_year_month.items()):
#     print(f"\n=== ELEPHANT: {elephant_id.upper()} ===")
#     for year, month_dict in sorted(year_dict.items()):
#         print(f"\n   YEAR {year} → {len(month_dict)} month(s) found")

#         # ---- sanity check -------------------------------------------------
#         sample = next(iter(month_dict.values()))
#         missing = {'Latitude', 'Longitude'} - set(sample.columns)
#         if missing:
#             print(f"      → SKIP elephant {elephant_id} year {year}: missing columns {missing}")
#             continue

#         # ---- output folder (one folder per elephant) --------------------
#         elephant_out = os.path.join(OUT_ROOT, elephant_id.upper())
#         ensure_folder(elephant_out)

#         # ---- generate ONE map per month ---------------------------------
#         monthly_html = {}   # month → filename (relative to elephant_out)

#         for month in range(1, 13):
#             if month not in month_dict:
#                 print(f"      month {month:02d} → no data")
#                 continue

#             df_m = month_dict[month]
#             if df_m.empty:
#                 print(f"      month {month:02d} → empty after cleaning")
#                 continue

#             lat_c = df_m['Latitude'].mean()
#             lon_c = df_m['Longitude'].mean()
#             print(f"      month {month:02d} centre [{lat_c:.5f}, {lon_c:.5f}]")

#             m = folium.Map(location=[lat_c, lon_c],
#                            zoom_start=ZOOM_START,
#                            tiles='OpenStreetMap')

#             colour = MONTH_COLORS[month]
#             pts = 0
#             for _, r in df_m.iterrows():
#                 if pd.isna(r['Latitude']) or pd.isna(r['Longitude']):
#                     continue
#                 folium.CircleMarker(
#                     location=[r['Latitude'], r['Longitude']],
#                     radius=5,
#                     color=colour,
#                     fill=True,
#                     fill_color=colour,
#                     popup=f"{r['DateTime']}<br>Month {month}"
#                 ).add_to(m)
#                 pts += 1

#             if pts == 0:
#                 print(f"      month {month:02d} → no valid points")
#                 continue

#             map_name = f"{elephant_id.upper()}_{year}_M{month:02d}_{MONTH_NAMES[month-1]}.html"
#             map_path = os.path.join(elephant_out, map_name)
#             m.save(map_path)
#             monthly_html[month] = map_name
#             print(f"      → saved {map_name} ({pts} pts)")

#         # ---- build the 3×4 grid if we have at least one map -------------
#         if not monthly_html:
#             print(f"   elephant {elephant_id} year {year} → NO MAPS → skip grid")
#             continue

#         any_grid_created = True
#         grid_html = f"""<!DOCTYPE html>
# <html><head><meta charset="utf-8">
# <title>{elephant_id.upper()} {year} – 12‑Month Grid</title>
# <style>
#   body{{font-family:Arial;margin:20px}}
#   h1{{text-align:center}}
#   .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:1500px;margin:auto}}
#   .box{{border:1px solid #aaa;padding:8px;text-align:center;background:#fff}}
#   .box h3{{margin:4px 0}}
#   iframe{{width:100%;height:{MAP_HEIGHT_PX}px;border:0}}
#   .miss{{background:#f8f8f8;color:#999;padding:40px}}
# </style></head><body>
# <h1>{elephant_id.upper()} – {year} (12‑Month Grid)</h1>
# <div class="grid">
# """

#         for m in range(1, 13):
#             name = MONTH_NAMES[m-1]
#             if m in monthly_html:
#                 grid_html += f"""<div class="box"><h3>{name}</h3>
# <iframe src="{monthly_html[m]}"></iframe></div>"""
#             else:
#                 grid_html += f"""<div class="box miss"><h3>{name}</h3>
# <p>No data</p></div>"""

#         grid_html += "\n</div></body></html>"

#         grid_file = f"{elephant_id.upper()}_{year}_12_Months_Grid.html"
#         grid_path = os.path.join(elephant_out, grid_file)
#         with open(grid_path, 'w', encoding='utf-8') as f:
#             f.write(grid_html)

#         print(f"   GRID SAVED → {grid_file}")

# # ----------------------------------------------------------------------
# # 4. FINAL SUMMARY
# # ----------------------------------------------------------------------
# print("\n=== DONE ===")
# if any_grid_created:
#     print(f"Success: Grids created under {os.path.abspath(OUT_ROOT)}")
# else:
#     print("Warning: NO grid was produced – check the debug messages above.")

# import os
# import re
# import pandas as pd
# import folium
# from collections import defaultdict

# # ----------------------------------------------------------------------
# # 1. SETTINGS
# # ----------------------------------------------------------------------
# IN_FOLDER        = "../Filter_By_Month"          # <-- folder that contains occ sub‑folders
# OUT_ROOT         = "../maps_months"              # <-- where everything will be written
# ZOOM_START       = 9
# MAP_HEIGHT_PX    = 250

# MONTH_COLORS = {
#     1: '#008000', 2: '#FF0000', 3: '#0000FF', 4: '#800080',
#     5: '#FFA500', 6: '#00FFFF', 7: '#FFFF00', 8: '#FF00FF',
#     9: '#A52A2A',10: '#808080',11: '#000080',12: '#FFC0CB'
# }
# MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun',
#                'Jul','Aug','Sep','Oct','Nov','Dec']

# # ----------------------------------------------------------------------
# # 2. HELPER
# # ----------------------------------------------------------------------
# def ensure_folder(p):
#     if not os.path.isdir(p):
#         os.makedirs(p, exist_ok=True)
#         print(f"   Created folder: {p}")

# def get_color_gradient(day):
#     """Generate a color from red to green to blue based on day (1-31)."""
#     fraction = (day - 1) / 30.0  # Normalize to 0-1
#     if fraction < 0.5:
#         # Red to green
#         sub_frac = fraction / 0.5
#         r = int(255 * (1 - sub_frac))
#         g = int(255 * sub_frac)
#         b = 0
#     else:
#         # Green to blue
#         sub_frac = (fraction - 0.5) / 0.5
#         r = 0
#         g = int(255 * (1 - sub_frac))
#         b = int(255 * sub_frac)
#     return f'#{r:02x}{g:02x}{b:02x}'

# # ----------------------------------------------------------------------
# # 3. MAIN
# # ----------------------------------------------------------------------
# print(f"\n=== STARTING PROCESSING ===")
# print(f"Input folder : {os.path.abspath(IN_FOLDER)}")
# print(f"Output root  : {os.path.abspath(OUT_ROOT)}\n")

# if not os.path.isdir(IN_FOLDER):
#     raise SystemExit(f"ERROR: Input folder does not exist → {IN_FOLDER}")

# any_grid_created = False

# # ----------------------------------------------------------------------
# #   3.1  Walk every occ folder and collect *all* CSV files
# # ----------------------------------------------------------------------
# elephant_to_year_month = defaultdict(lambda: defaultdict(dict))   # elephant → year → month → df

# # regex to extract elephant ID (e.g. 01fe, 02me …)
# ELEPHANT_RE = re.compile(r'^(\d{2}[a-z]{2})')   # first two digits + two letters

# for occ in sorted(os.listdir(IN_FOLDER)):
#     occ_path = os.path.join(IN_FOLDER, occ)
#     if not os.path.isdir(occ_path):
#         print(f"   Skipping non‑folder: {occ}")
#         continue

#     print(f"\n--- OCCURRENCE FOLDER: {occ} ---")
#     csv_files = [f for f in os.listdir(occ_path) if f.lower().endswith('.csv')]
#     if not csv_files:
#         print(f"   No *.csv files in {occ_path}")
#         continue

#     for fname in csv_files:
#         print(f"   Examining file: {fname}")

#         # ---- 3.2  Extract elephant ID ---------------------------------
#         m_id = ELEPHANT_RE.search(fname)
#         if not m_id:
#             print(f"      → cannot extract elephant ID (need 01fe/02me … at start)")
#             continue
#         elephant_id = m_id.group(1).lower()
#         print(f"      → belongs to elephant '{elephant_id}'")

#         # ---- 3.3  Parse year‑month from the *last* two '_' parts -----
#         parts = fname.rsplit('_', 2)
#         if len(parts) != 3 or not parts[2].endswith('.csv'):
#             print(f"      → cannot parse (need 2 '_' before .csv)")
#             continue

#         period = parts[2].replace('.csv', '')
#         if '-' not in period:
#             print(f"      → period part has no '-'")
#             continue

#         try:
#             file_year  = int(period.split('-')[0])
#             file_month = int(period.split('-')[1])
#         except ValueError:
#             print(f"      → cannot convert year/month to int")
#             continue

#         if not (1 <= file_month <= 12):
#             print(f"      → month {file_month} out of range")
#             continue

#         # ---- 3.4  Load CSV -------------------------------------------
#         fp = os.path.join(occ_path, fname)
#         try:
#             df = pd.read_csv(fp)
#         except Exception as e:
#             print(f"      → FAILED to read CSV: {e}")
#             continue

#         print(f"      rows before dropna: {len(df)}")
#         df.dropna(subset=['Latitude', 'Longitude', 'Date', 'Time'], inplace=True)
#         print(f"      rows after  dropna: {len(df)}")
#         if df.empty:
#             print(f"      → empty after cleaning")
#             continue

#         # ---- 3.5  Add datetime column --------------------------------
#         df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
#         df['Month']    = file_month

#         # ---- 3.6  Store -----------------------------------------------
#         if file_month in elephant_to_year_month[elephant_id][file_year]:
#             elephant_to_year_month[elephant_id][file_year][file_month] = pd.concat(
#                 [elephant_to_year_month[elephant_id][file_year][file_month], df],
#                 ignore_index=True)
#         else:
#             elephant_to_year_month[elephant_id][file_year][file_month] = df

#         print(f"      → stored as elephant {elephant_id} | year {file_year} | month {file_month}")

# # ----------------------------------------------------------------------
# #   3.7  For every elephant → every year → build ONE 12‑month grid
# # ----------------------------------------------------------------------
# for elephant_id, year_dict in sorted(elephant_to_year_month.items()):
#     print(f"\n=== ELEPHANT: {elephant_id.upper()} ===")
#     for year, month_dict in sorted(year_dict.items()):
#         print(f"\n   YEAR {year} → {len(month_dict)} month(s) found")

#         # ---- sanity check -------------------------------------------------
#         sample = next(iter(month_dict.values()))
#         missing = {'Latitude', 'Longitude'} - set(sample.columns)
#         if missing:
#             print(f"      → SKIP elephant {elephant_id} year {year}: missing columns {missing}")
#             continue

#         # ---- output folder (one folder per elephant) --------------------
#         elephant_out = os.path.join(OUT_ROOT, elephant_id.upper())
#         ensure_folder(elephant_out)

#         # ---- generate ONE map per month ---------------------------------
#         monthly_html = {}   # month → filename (relative to elephant_out)

#         for month in range(1, 13):
#             if month not in month_dict:
#                 print(f"      month {month:02d} → no data")
#                 continue

#             df_m = month_dict[month]
#             if df_m.empty:
#                 print(f"      month {month:02d} → empty after cleaning")
#                 continue

#             lat_c = df_m['Latitude'].mean()
#             lon_c = df_m['Longitude'].mean()
#             print(f"      month {month:02d} centre [{lat_c:.5f}, {lon_c:.5f}]")

#             m = folium.Map(location=[lat_c, lon_c],
#                            zoom_start=ZOOM_START,
#                            tiles='OpenStreetMap')

#             pts = 0
#             for _, r in df_m.iterrows():
#                 if pd.isna(r['DateTime']) or pd.isna(r['Latitude']) or pd.isna(r['Longitude']):
#                     continue
#                 day = r['DateTime'].day
#                 colour = get_color_gradient(day)
#                 folium.CircleMarker(
#                     location=[r['Latitude'], r['Longitude']],
#                     radius=5,
#                     color=colour,
#                     fill=True,
#                     fill_color=colour,
#                     popup=f"{r['DateTime']}<br>Month {month} (Day {day})"
#                 ).add_to(m)
#                 pts += 1

#             if pts == 0:
#                 print(f"      month {month:02d} → no valid points")
#                 continue

#             map_name = f"{elephant_id.upper()}_{year}_M{month:02d}_{MONTH_NAMES[month-1]}.html"
#             map_path = os.path.join(elephant_out, map_name)
#             m.save(map_path)
#             monthly_html[month] = map_name
#             print(f"      → saved {map_name} ({pts} pts)")

#         # ---- build the 3×4 grid if we have at least one map -------------
#         if not monthly_html:
#             print(f"   elephant {elephant_id} year {year} → NO MAPS → skip grid")
#             continue

#         any_grid_created = True
#         grid_html = f"""<!DOCTYPE html>
# <html><head><meta charset="utf-8">
# <title>{elephant_id.upper()} {year} – 12‑Month Grid</title>
# <style>
#   body{{font-family:Arial;margin:20px}}
#   h1{{text-align:center}}
#   .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:1500px;margin:auto}}
#   .box{{border:1px solid #aaa;padding:8px;text-align:center;background:#fff}}
#   .box h3{{margin:4px 0}}
#   iframe{{width:100%;height:{MAP_HEIGHT_PX}px;border:0}}
#   .miss{{background:#f8f8f8;color:#999;padding:40px}}
# </style></head><body>
# <h1>{elephant_id.upper()} – {year} (12‑Month Grid)</h1>
# <div class="grid">
# """

#         for m in range(1, 13):
#             name = MONTH_NAMES[m-1]
#             if m in monthly_html:
#                 grid_html += f"""<div class="box"><h3>{name}</h3>
# <iframe src="{monthly_html[m]}"></iframe></div>"""
#             else:
#                 grid_html += f"""<div class="box miss"><h3>{name}</h3>
# <p>No data</p></div>"""

#         grid_html += "\n</div></body></html>"

#         grid_file = f"{elephant_id.upper()}_{year}_12_Months_Grid.html"
#         grid_path = os.path.join(elephant_out, grid_file)
#         with open(grid_path, 'w', encoding='utf-8') as f:
#             f.write(grid_html)

#         print(f"   GRID SAVED → {grid_file}")

# # ----------------------------------------------------------------------
# # 4. FINAL SUMMARY
# # ----------------------------------------------------------------------
# print("\n=== DONE ===")
# if any_grid_created:
#     print(f"Success: Grids created under {os.path.abspath(OUT_ROOT)}")
# else:
#     print("Warning: NO grid was produced – check the debug messages above.")

import os
import re
import pandas as pd
import folium
from collections import defaultdict

# ----------------------------------------------------------------------
# 1. SETTINGS
# ----------------------------------------------------------------------
IN_FOLDER        = "../Filter_By_Month"          # <-- folder that contains occ sub‑folders
OUT_ROOT         = "../maps_months"              # <-- where everything will be written
ZOOM_START       = 9
MAP_HEIGHT_PX    = 250

MONTH_COLORS = {
    1: '#008000', 2: '#FF0000', 3: '#0000FF', 4: '#800080',
    5: '#FFA500', 6: '#00FFFF', 7: '#FFFF00', 8: '#FF00FF',
    9: '#A52A2A',10: '#808080',11: '#000080',12: '#FFC0CB'
}
MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']

PALETTE = [
    "#DEFCFC", '#CAF0F8', '#ADE8F4', '#90E0EF', '#48CAE4',
    '#00B4D8', '#0096C7', '#0077B6', '#023E8A', '#03045E'
]

# ----------------------------------------------------------------------
# 2. HELPER
# ----------------------------------------------------------------------
def ensure_folder(p):
    if not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)
        print(f"   Created folder: {p}")

def hex_to_rgb(hex_str):
    """Convert hex color to RGB tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color."""
    return '#%02x%02x%02x' % rgb

def get_color_gradient(day):
    """Generate a color from the pastel greenery palette based on day (1-31)."""
    fraction = (day - 1) / 30.0  # Normalize to 0-1
    n_colors = len(PALETTE)
    idx = int(fraction * (n_colors - 1))
    if idx >= n_colors - 1:
        return PALETTE[-1]
    frac = (fraction * (n_colors - 1)) - idx
    c1 = hex_to_rgb(PALETTE[idx])
    c2 = hex_to_rgb(PALETTE[idx + 1])
    r = int(c1[0] + frac * (c2[0] - c1[0]))
    g = int(c1[1] + frac * (c2[1] - c1[1]))
    b = int(c1[2] + frac * (c2[2] - c1[2]))
    return rgb_to_hex((r, g, b))

# ----------------------------------------------------------------------
# 3. MAIN
# ----------------------------------------------------------------------
print(f"\n=== STARTING PROCESSING ===")
print(f"Input folder : {os.path.abspath(IN_FOLDER)}")
print(f"Output root  : {os.path.abspath(OUT_ROOT)}\n")

if not os.path.isdir(IN_FOLDER):
    raise SystemExit(f"ERROR: Input folder does not exist → {IN_FOLDER}")

any_grid_created = False

# ----------------------------------------------------------------------
#   3.1  Walk every occ folder and collect *all* CSV files
# ----------------------------------------------------------------------
elephant_to_year_month = defaultdict(lambda: defaultdict(dict))   # elephant → year → month → df

# regex to extract elephant ID (e.g. 01fe, 02me …)
ELEPHANT_RE = re.compile(r'^(\d{2}[a-z]{2})')   # first two digits + two letters

for occ in sorted(os.listdir(IN_FOLDER)):
    occ_path = os.path.join(IN_FOLDER, occ)
    if not os.path.isdir(occ_path):
        print(f"   Skipping non‑folder: {occ}")
        continue

    print(f"\n--- OCCURRENCE FOLDER: {occ} ---")
    csv_files = [f for f in os.listdir(occ_path) if f.lower().endswith('.csv')]
    if not csv_files:
        print(f"   No *.csv files in {occ_path}")
        continue

    for fname in csv_files:
        print(f"   Examining file: {fname}")

        # ---- 3.2  Extract elephant ID ---------------------------------
        m_id = ELEPHANT_RE.search(fname)
        if not m_id:
            print(f"      → cannot extract elephant ID (need 01fe/02me … at start)")
            continue
        elephant_id = m_id.group(1).lower()
        print(f"      → belongs to elephant '{elephant_id}'")

        # ---- 3.3  Parse year‑month from the *last* two '_' parts -----
        parts = fname.rsplit('_', 2)
        if len(parts) != 3 or not parts[2].endswith('.csv'):
            print(f"      → cannot parse (need 2 '_' before .csv)")
            continue

        period = parts[2].replace('.csv', '')
        if '-' not in period:
            print(f"      → period part has no '-'")
            continue

        try:
            file_year  = int(period.split('-')[0])
            file_month = int(period.split('-')[1])
        except ValueError:
            print(f"      → cannot convert year/month to int")
            continue

        if not (1 <= file_month <= 12):
            print(f"      → month {file_month} out of range")
            continue

        # ---- 3.4  Load CSV -------------------------------------------
        fp = os.path.join(occ_path, fname)
        try:
            df = pd.read_csv(fp)
        except Exception as e:
            print(f"      → FAILED to read CSV: {e}")
            continue

        print(f"      rows before dropna: {len(df)}")
        df.dropna(subset=['Latitude', 'Longitude', 'Date', 'Time'], inplace=True)
        print(f"      rows after  dropna: {len(df)}")
        if df.empty:
            print(f"      → empty after cleaning")
            continue

        # ---- 3.5  Add datetime column --------------------------------
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        df['Month']    = file_month

        # ---- 3.6  Store -----------------------------------------------
        if file_month in elephant_to_year_month[elephant_id][file_year]:
            elephant_to_year_month[elephant_id][file_year][file_month] = pd.concat(
                [elephant_to_year_month[elephant_id][file_year][file_month], df],
                ignore_index=True)
        else:
            elephant_to_year_month[elephant_id][file_year][file_month] = df

        print(f"      → stored as elephant {elephant_id} | year {file_year} | month {file_month}")

# ----------------------------------------------------------------------
#   3.7  For every elephant → every year → build ONE 12‑month grid
# ----------------------------------------------------------------------
for elephant_id, year_dict in sorted(elephant_to_year_month.items()):
    print(f"\n=== ELEPHANT: {elephant_id.upper()} ===")
    for year, month_dict in sorted(year_dict.items()):
        print(f"\n   YEAR {year} → {len(month_dict)} month(s) found")

        # ---- sanity check -------------------------------------------------
        sample = next(iter(month_dict.values()))
        missing = {'Latitude', 'Longitude'} - set(sample.columns)
        if missing:
            print(f"      → SKIP elephant {elephant_id} year {year}: missing columns {missing}")
            continue

        # ---- output folder (one folder per elephant) --------------------
        elephant_out = os.path.join(OUT_ROOT, elephant_id.upper())
        ensure_folder(elephant_out)

        # ---- generate ONE map per month ---------------------------------
        monthly_html = {}   # month → filename (relative to elephant_out)

        for month in range(1, 13):
            if month not in month_dict:
                print(f"      month {month:02d} → no data")
                continue

            df_m = month_dict[month]
            if df_m.empty:
                print(f"      month {month:02d} → empty after cleaning")
                continue

            lat_c = df_m['Latitude'].mean()
            lon_c = df_m['Longitude'].mean()
            print(f"      month {month:02d} centre [{lat_c:.5f}, {lon_c:.5f}]")

            m = folium.Map(location=[lat_c, lon_c],
                           zoom_start=ZOOM_START,
                           tiles='OpenStreetMap')

            pts = 0
            for _, r in df_m.iterrows():
                if pd.isna(r['DateTime']) or pd.isna(r['Latitude']) or pd.isna(r['Longitude']):
                    continue
                day = r['DateTime'].day
                colour = get_color_gradient(day)
                folium.CircleMarker(
                    location=[r['Latitude'], r['Longitude']],
                    radius=5,
                    color=colour,
                    fill=True,
                    fill_color=colour,
                    popup=f"{r['DateTime']}<br>Month {month} (Day {day})"
                ).add_to(m)
                pts += 1

            if pts == 0:
                print(f"      month {month:02d} → no valid points")
                continue

            map_name = f"{elephant_id.upper()}_{year}_M{month:02d}_{MONTH_NAMES[month-1]}.html"
            map_path = os.path.join(elephant_out, map_name)
            m.save(map_path)
            monthly_html[month] = map_name
            print(f"      → saved {map_name} ({pts} pts)")

        # ---- build the 3×4 grid if we have at least one map -------------
        if not monthly_html:
            print(f"   elephant {elephant_id} year {year} → NO MAPS → skip grid")
            continue

        any_grid_created = True
        grid_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{elephant_id.upper()} {year} – 12‑Month Grid</title>
<style>
  body{{font-family:Arial;margin:20px}}
  h1{{text-align:center}}
  .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:1500px;margin:auto}}
  .box{{border:1px solid #aaa;padding:8px;text-align:center;background:#fff}}
  .box h3{{margin:4px 0}}
  iframe{{width:100%;height:{MAP_HEIGHT_PX}px;border:0}}
  .miss{{background:#f8f8f8;color:#999;padding:40px}}
</style></head><body>
<h1>{elephant_id.upper()} – {year} (12‑Month Grid)</h1>
<div class="grid">
"""

        for m in range(1, 13):
            name = MONTH_NAMES[m-1]
            if m in monthly_html:
                grid_html += f"""<div class="box"><h3>{name}</h3>
<iframe src="{monthly_html[m]}"></iframe></div>"""
            else:
                grid_html += f"""<div class="box miss"><h3>{name}</h3>
<p>No data</p></div>"""

        grid_html += "\n</div></body></html>"

        grid_file = f"{elephant_id.upper()}_{year}_12_Months_Grid.html"
        grid_path = os.path.join(elephant_out, grid_file)
        with open(grid_path, 'w', encoding='utf-8') as f:
            f.write(grid_html)

        print(f"   GRID SAVED → {grid_file}")

# ----------------------------------------------------------------------
# 4. FINAL SUMMARY
# ----------------------------------------------------------------------
print("\n=== DONE ===")
if any_grid_created:
    print(f"Success: Grids created under {os.path.abspath(OUT_ROOT)}")
else:
    print("Warning: NO grid was produced – check the debug messages above.")