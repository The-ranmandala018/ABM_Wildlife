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


# # Define paths (adjust if needed for exact file structure)
# base_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data'
# save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_StayDuration'
# fe_path = os.path.join(base_path, 'fe')
# me_path = os.path.join(base_path, 'me')
# waterholes_path = os.path.join(base_path, 'Waterholes.csv')
# weather_path = os.path.join(base_path, 'okaukuejo_weather_all_years.csv')
# plots_dir = os.path.join(save_path, 'analysis1')

# # Create plots directory if it doesn't exist
# os.makedirs(plots_dir, exist_ok=True)

# # Load waterholes data with encoding fix
# waterholes = pd.read_csv(waterholes_path, encoding='latin-1')
# waterholes['lat'] = waterholes['Latitude']
# waterholes['lon'] = waterholes['Longitude']

# # Load elephant data from all CSV files in fe and me folders
# elephant_files = glob.glob(os.path.join(fe_path, '*.csv')) + glob.glob(os.path.join(me_path, '*.csv'))
# if not elephant_files:
#     print("No CSV files found in fe or me directories.")
# else:
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
   
#     # Drop 'individual-local-identifier' if present
#     if 'individual-local-identifier' in ele_data.columns:
#         ele_data = ele_data.drop(columns=['individual-local-identifier'])
   
#     # Parse DateTime (assuming 'Date' and 'Time'/'timeAPM' exist)
#     time_col = 'Time' if 'Time' in ele_data.columns else 'timeAPM'
#     ele_data['DateTime'] = pd.to_datetime(ele_data['Date'] + ' ' + ele_data[time_col])
   
#     # Extract date/time components
#     ele_data['year'] = ele_data['DateTime'].dt.year
#     ele_data['month'] = ele_data['DateTime'].dt.month
#     ele_data['hour'] = ele_data['DateTime'].dt.hour + (ele_data['DateTime'].dt.minute / 60.0)
#     ele_data['date'] = ele_data['DateTime'].dt.date
   
#     # Load and integrate weather data
#     try:
#         weather = pd.read_csv(weather_path, encoding='utf-8')
#     except UnicodeDecodeError:
#         weather = pd.read_csv(weather_path, encoding='latin-1')
   
#     weather['date'] = pd.to_datetime(weather['Date']).dt.date
#     temp_dict = dict(zip(weather['date'], weather['Temp_C']))
#     humidity_dict = dict(zip(weather['date'], weather['Humidity_%']))
#     ele_data['Temp_C'] = ele_data['date'].map(temp_dict)
#     ele_data['Humidity_%'] = ele_data['date'].map(humidity_dict)
   
#     # Define radius for proximity (km)
#     radius = 1.0
   
#     # Assign waterholes to elephant observations
#     print("Assigning waterholes to elephant observations (vectorized)...")
#     ele_lons = ele_data['Longitude'].values
#     ele_lats = ele_data['Latitude'].values
#     wh_lons = waterholes['lon'].values
#     wh_lats = waterholes['lat'].values
   
#     dist_matrix = haversine_vectorized(ele_lons, ele_lats, wh_lons, wh_lats)
   
#     # Find min dist and closest index for each elephant observation
#     min_dists = np.min(dist_matrix, axis=1)
#     closest_idxs = np.argmin(dist_matrix, axis=1)
   
#     # Assign waterhole if within radius
#     wh_names = waterholes['Name'].values
#     ele_data['waterhole'] = np.where(min_dists <= radius, wh_names[closest_idxs], np.nan)
   
#     # Drop rows missing key data
#     ele_data = ele_data.dropna(subset=['waterhole', 'Temp_C', 'Humidity_%'])
   
#     # Get unique individuals
#     individuals = sorted(ele_data['elephant_id'].unique())
#     print(f"Processing {len(individuals)} individuals...")
   
#     # Process for each elephant and year separately
#     for ind in individuals:
#         ind_data = ele_data[ele_data['elephant_id'] == ind].copy()
#         unique_years = sorted(ind_data['year'].unique())
        
#         for year in unique_years:
#             year_data = ind_data[ind_data['year'] == year].copy()
#             if len(year_data) == 0:
#                 continue
            
#             year_data = year_data.sort_values('DateTime').reset_index(drop=True)
            
#             # Group by date and waterhole
#             daily_stay_groups = year_data.groupby(['date', 'waterhole'])
#             stays_list = []
            
#             for (date_obj, wh), group in daily_stay_groups:
#                 if len(group) > 0:
#                     start_time = group['DateTime'].min()
#                     end_time = group['DateTime'].max()
#                     duration_hours = (end_time - start_time).total_seconds() / 3600.0
#                     temp_c = group['Temp_C'].iloc[0]
#                     humidity_percent = group['Humidity_%'].iloc[0]
                    
#                     #  Include Season column
#                     if 'Season' in group.columns:
#                         season = group['Season'].iloc[0]
#                     else:
#                         season = np.nan
                    
#                     # Get waterhole lon/lat
#                     wh_info = waterholes[waterholes['Name'] == wh].iloc[0]
#                     lon = wh_info['lon']
#                     lat = wh_info['lat']
                    
#                     date_str = date_obj.strftime('%Y-%m-%d')
                    
#                     stays_list.append({
#                         'elephant_id': ind,
#                         'year': year,
#                         'date': date_str,
#                         'season': season,
#                         'waterhole': wh,
#                         'lon': lon,
#                         'lat': lat,
#                         'start_time': start_time,
#                         'end_time': end_time,
#                         'stay_duration_hours': duration_hours,
#                         'temp_c': temp_c,
#                         'humidity_percent': humidity_percent
#                     })
            
#             if stays_list:
#                 stays_df = pd.DataFrame(stays_list)
#                 stays_df['start_time_str'] = stays_df['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
#                 stays_df['end_time_str'] = stays_df['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
#                 # Include Season in output
#                 output_cols = [
#                     'elephant_id', 'year', 'season', 'date', 'waterhole',
#                     'lon', 'lat', 'start_time_str', 'end_time_str',
#                     'stay_duration_hours', 'temp_c', 'humidity_percent'
#                 ]
                
#                 stays_df = stays_df[output_cols]
                
#                 # Save CSV
#                 filename = f'{ind}_{year}_daily_waterhole_stays.csv'
#                 path = os.path.join(plots_dir, filename)
#                 stays_df.to_csv(path, index=False)
#                 print(f"Saved daily waterhole stays CSV for {ind} - {year}: {path}")
#             else:
#                 print(f"No daily stays found for {ind} - {year}")
   
#     print("All individual elephant-year daily waterhole stays CSV files saved to:", plots_dir)






# import pandas as pd
# import glob
# import numpy as np
# import os
# import matplotlib.pyplot as plt
# import matplotlib.colors as mcolors
# from calendar import month_abbr  # For month names
# import seaborn as sns
# from scipy import stats
# from datetime import datetime
# # Define paths (using your exact full paths) - Ensure no extra spaces or typos
# old_plots_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_StayDuration\analysis1'
# new_save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_StayDuration'
# analysis_dir = os.path.join(new_save_path, 'stay_analysis1')
# weather_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\okaukuejo_weather_all_years.csv'  # Add weather path
# # Debug: Print and normalize paths
# print(f"Working directory: {os.getcwd()}")
# print(f"Loading stays from: {old_plots_dir}")
# print(f"Raw analysis_dir: {analysis_dir}")
# # Normalize path to handle any Windows quirks
# analysis_dir = os.path.normpath(analysis_dir)
# print(f"Normalized analysis_dir: {analysis_dir}")
# # Step-by-step path verification
# parent_dir = os.path.dirname(analysis_dir)
# print(f"Parent directory: {parent_dir}")
# print(f"Parent exists: {os.path.exists(parent_dir)}")
# # Load weather data once (outside loop)
# try:
#     weather = pd.read_csv(weather_path, encoding='utf-8')
# except UnicodeDecodeError:
#     weather = pd.read_csv(weather_path, encoding='latin-1')
# weather['date'] = pd.to_datetime(weather['Date']).dt.date
# precip_dict = dict(zip(weather['date'], weather['Precip_mm']))
# # Load all daily waterhole stays CSVs from old directory and process per elephant-year
# stay_files = glob.glob(os.path.join(old_plots_dir, '*_daily_waterhole_stays.csv'))
# print(f"Found {len(stay_files)} stay files in {old_plots_dir}")
# if not stay_files:
#     print("No stay CSV files found in:", old_plots_dir)
#     exit()
# # Create analysis directory step by step
# os.makedirs(new_save_path, exist_ok=True)
# print(f"Created/verified base save path: {new_save_path}")
# os.makedirs(analysis_dir, exist_ok=True)
# print(f"Created/verified analysis_dir: {analysis_dir}")
# for f in stay_files:
#     # Load per elephant-year CSV
#     df = pd.read_csv(f)
#     # Improved filename parsing for stays file: {elephant_id}_{year}_daily_waterhole_stays.csv
#     filename_base = os.path.basename(f).replace('.csv', '')
#     parts = filename_base.split('_')
#     elephant_id = parts[0]
#     year = parts[1]  # Second part is year (before 'daily...')
#     print(f"\nProcessing {elephant_id} - {year} (from file: {filename_base})")
    
#     # Use existing 'season' column from the loaded stays CSV (already populated from original data)
#     # Assume it's uniform per elephant-year; take the first non-null value
#     if 'season' in df.columns and not df['season'].isna().all():
#         season = df['season'].dropna().iloc[0]  # Use first non-null
#         print(f"  Using season from stays data: {season}")
#     else:
#         season = 'unknown'
#         print(f"  Warning: No valid season in stays data; using 'unknown'")
    
#     # Map Precip_mm from weather by date
#     df['date'] = pd.to_datetime(df['date']).dt.date  # Ensure date column is date type
#     df['Precip_mm'] = df['date'].map(precip_dict)
    
#     # Drop rows with missing Precip_mm
#     df = df.dropna(subset=['Precip_mm'])
    
#     # Parse start_time_str to extract hour
#     df['start_hour'] = pd.to_datetime(df['start_time_str']).dt.hour
    
#     # Basic statistics (now including Precip_mm and season)
#     print("\nBasic Statistics:")
#     stats_desc = df[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].describe()
#     print(stats_desc)
    
#     # Correlations (now including Precip_mm)
#     corr_matrix = df[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].corr()
#     print("\nCorrelation Matrix:")
#     print(corr_matrix)
    
#     # Linear regression (now including Precip_mm, with check for identical values)
#     if len(df) > 1:
#         slope_temp, intercept_temp, r_temp, p_temp, std_err_temp = stats.linregress(df['temp_c'], df['stay_duration_hours'])
#         slope_hum, intercept_hum, r_hum, p_hum, std_err_hum = stats.linregress(df['humidity_percent'], df['stay_duration_hours'])
        
#         print(f"\nLinear Regression Results:")
#         print(f"Stay Duration ~ Temp_C: slope={slope_temp:.4f}, r={r_temp:.4f}, p={p_temp:.4f}")
#         print(f"Stay Duration ~ Humidity_%: slope={slope_hum:.4f}, r={r_hum:.4f}, p={p_hum:.4f}")
        
#         # Check for Precip_mm regression - skip if all values identical (variance=0)
#         if df['Precip_mm'].std() > 0 and df['Precip_mm'].nunique() > 1:
#             slope_precip, intercept_precip, r_precip, p_precip, std_err_precip = stats.linregress(df['Precip_mm'], df['stay_duration_hours'])
#             print(f"Stay Duration ~ Precip_mm: slope={slope_precip:.4f}, r={r_precip:.4f}, p={p_precip:.4f}")
#         else:
#             print("Skipping Precip regression: all Precip_mm values are identical (likely 0 mm in dry season).")
#             slope_precip, intercept_precip, r_precip, p_precip, std_err_precip = np.nan, np.nan, np.nan, np.nan, np.nan  # Set to NaN for plotting
#     else:
#         print("\nInsufficient data for regression.")
#         slope_temp, intercept_temp, r_temp, p_temp = np.nan, np.nan, np.nan, np.nan
#         slope_hum, intercept_hum, r_hum, p_hum = np.nan, np.nan, np.nan, np.nan
#         slope_precip, intercept_precip, r_precip, p_precip = np.nan, np.nan, np.nan, np.nan
    
#     # Define thresholds (per elephant-year) - now including precip
#     temp_high_thresh = df['temp_c'].quantile(0.75)
#     hum_low_thresh = df['humidity_percent'].quantile(0.25)
#     precip_high_thresh = df['Precip_mm'].quantile(0.75)  # High precip threshold
#     stay_high_thresh = df['stay_duration_hours'].median()  # High stay as above median
    
#     print(f"\nHigh Temp Threshold (> {temp_high_thresh:.1f}°C), Low Humidity Threshold (< {hum_low_thresh:.1f}%)")
#     print(f"High Precip Threshold (> {precip_high_thresh:.1f} mm)")
#     print(f"High Stay Threshold (> {stay_high_thresh:.2f} hours)")
    
#     # Overall average stay
#     avg_stay_all = df['stay_duration_hours'].mean()
#     print(f"Average stay duration overall: {avg_stay_all:.2f} hours")
    
#     # Filter for high temp low humidity (keep as is, or add precip filter if needed)
#     high_temp_low_hum = df[(df['temp_c'] > temp_high_thresh) & (df['humidity_percent'] < hum_low_thresh)]
#     if len(high_temp_low_hum) > 0:
#         avg_stay_high_low = high_temp_low_hum['stay_duration_hours'].mean()
#         print(f"Average stay duration under high temp & low humidity: {avg_stay_high_low:.2f} hours")
#         print(f"Number of such stays: {len(high_temp_low_hum)}")
        
#         # Start hour distribution
#         hour_dist = high_temp_low_hum['start_hour'].value_counts().sort_index()
#         print("\nStart hour distribution under high temp & low humidity:")
#         print(hour_dist)
        
#         # Overall start hour distribution
#         hour_dist_all = df['start_hour'].value_counts().sort_index()
#         print("\nStart hour distribution overall:")
#         print(hour_dist_all)
#     else:
#         print("No stays found under high temp & low humidity conditions.")
    
#     # Add categorical columns (now including precip_cat)
#     df['temp_cat'] = pd.cut(df['temp_c'], bins=3, labels=['Low', 'Med', 'High'])
#     df['hum_cat'] = pd.cut(df['humidity_percent'], bins=3, labels=['Low', 'Med', 'High'])
#     df['precip_cat'] = pd.cut(df['Precip_mm'], bins=3, labels=['Low', 'Med', 'High'])
#     df['stay_cat'] = np.where(df['stay_duration_hours'] > stay_high_thresh, 'High', 'Low')
#     df['condition'] = df['temp_cat'].astype(str) + ' Temp + ' + df['hum_cat'].astype(str) + ' Hum + ' + df['precip_cat'].astype(str) + ' Precip'
    
#     # Save enhanced CSV with renamed format including year (now with Precip_mm and season)
#     enhanced_csv_path = os.path.join(analysis_dir, f'{elephant_id}_stays_enhanced_stays_{year}.csv')
#     enhanced_cols = ['elephant_id', 'year', 'date', 'waterhole', 'lon', 'lat', 'start_time_str', 'end_time_str', 'stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm', 'start_hour', 'temp_cat', 'hum_cat', 'precip_cat', 'stay_cat', 'condition', 'season']
#     df[enhanced_cols].to_csv(enhanced_csv_path, index=False)
#     print(f"Saved enhanced CSV: {enhanced_csv_path}")
    
#     # Debug: Check if file exists and its size
#     if os.path.exists(enhanced_csv_path):
#         file_size = os.path.getsize(enhanced_csv_path)
#         print(f"✓ Confirmed: CSV exists at {enhanced_csv_path} (size: {file_size} bytes)")
#     else:
#         print(f"✗ Error: CSV not saved at {enhanced_csv_path}")
#         # Try alternative save with full path
#         try:
#             df[enhanced_cols].to_csv(enhanced_csv_path, index=False)
#             print(f"Retry successful: {enhanced_csv_path}")
#         except Exception as e:
#             print(f"Save error: {e}")
    
#     # Create per elephant-year plots directory with renamed format including year
#     elephant_year_plots = os.path.join(analysis_dir, f'{elephant_id}_stays_{year}')
#     os.makedirs(elephant_year_plots, exist_ok=True)
#     print(f"Created/verified plots dir: {elephant_year_plots}")
    
#     # Define 12 custom colors for months 1-12
#     month_colors_full = [
#         '#1E90FF', '#FF4500', '#32CD32', '#8A2BE2', '#FFD700', '#FFA500',
#         '#A9A9A9', '#00CED1', '#FF69B4', '#8B4513', '#008080', '#FF00FF'
#     ]
    
#     # Ensure month column is added (do this once per file)
#     df['date_dt'] = pd.to_datetime(df['date'])
#     df['month'] = df['date_dt'].dt.month
    
#     # Get available months only
#     available_months = sorted(df['month'].dropna().unique())
#     if not available_months:
#         print("No valid months found; skipping month-colored plots.")
#         # Continue to other plots...
#     else:
#         # Month names for available months
#         month_names_avail = [month_abbr[m][:3] for m in available_months]
        
#         # Custom colors (full 12, but slice for available)
#         month_colors_avail = [month_colors_full[m-1] for m in available_months]
#         custom_cmap_avail = mcolors.ListedColormap(month_colors_avail)
        
#         print(f"Available months: {month_names_avail}")
#         print(f"Corresponding colors: {month_colors_avail}")
#     # Plot 1: Scatter Stay vs Temp, colored by Humidity with Regression Line
#     plt.figure(figsize=(10, 6))
#     scatter = plt.scatter(df['temp_c'], df['stay_duration_hours'], c=df['humidity_percent'], cmap='viridis', alpha=0.6)
#     plt.colorbar(scatter, label='Humidity %')
#     plt.xlabel('Temperature (°C)')
#     plt.ylabel('Stay Duration (hours)')
#     plt.title(f'{elephant_id} - {year} ({season}): Stay Duration vs Temperature (colored by Humidity)')
    
#     # Add regression line for temp vs stay if valid
#     if not np.isnan(slope_temp):
#         x_line = np.linspace(df['temp_c'].min(), df['temp_c'].max(), 100)
#         y_line = slope_temp * x_line + intercept_temp
#         plt.plot(x_line, y_line, color='red', linestyle='--', linewidth=2, label='Regression Trend Line')
#         plt.legend()
    
#     plot_path1 = os.path.join(elephant_year_plots, f'{elephant_id}_stays_vs_temp_hum_{year}.png')
#     plt.savefig(plot_path1, dpi=300, bbox_inches='tight')
#     plt.close()
    
#     # Plot 1b: Line Chart for Stay Duration vs Temp (colored by Available Months)
#     plt.figure(figsize=(10, 6))
#     temp_sorted = df.sort_values('temp_c').copy()
#     if available_months:
#         temp_sorted['month_idx'] = temp_sorted['month'].map({m: i for i, m in enumerate(available_months)})  # Map to 0-len(avail)-1
#         # Plot connection line
#         plt.plot(temp_sorted['temp_c'], temp_sorted['stay_duration_hours'], color='gray', linestyle='-', alpha=0.5, linewidth=1, label='Connection Line')
#         # Scatter with available cmap (only colors for present months)
#         mask = temp_sorted['month'].isin(available_months)
#         if mask.sum() > 0:
#             scatter_month = plt.scatter(temp_sorted.loc[mask, 'temp_c'], temp_sorted.loc[mask, 'stay_duration_hours'],
#                                         c=temp_sorted.loc[mask, 'month_idx'], cmap=custom_cmap_avail, alpha=0.7, s=50,
#                                         edgecolors='black', linewidth=0.5)
#             # Colorbar with available months only
#             cbar = plt.colorbar(scatter_month, label='Month', ticks=range(len(available_months)))
#             cbar.set_ticklabels(month_names_avail)
#     plt.xlabel('Temperature (°C)')
#     plt.ylabel('Stay Duration (hours)')
#     plt.title(f'{elephant_id} - {year} ({season}): Line Chart - Stay Duration vs Temperature (colored by Month)')
#     plt.grid(True, alpha=0.3)
#     plt.legend()
#     plot_path1b = os.path.join(elephant_year_plots, f'{elephant_id}_line_stays_vs_temp_month_{year}.png')
#     plt.savefig(plot_path1b, dpi=300, bbox_inches='tight')
#     plt.close()
    
#     # Plot 2: Scatter Stay vs Humidity, colored by Temp with Regression Line
#     plt.figure(figsize=(10, 6))
#     scatter = plt.scatter(df['humidity_percent'], df['stay_duration_hours'], c=df['temp_c'], cmap='coolwarm', alpha=0.6)
#     plt.colorbar(scatter, label='Temperature (°C)')
#     plt.xlabel('Humidity (%)')
#     plt.ylabel('Stay Duration (hours)')
#     plt.title(f'{elephant_id} - {year} ({season}): Stay Duration vs Humidity (colored by Temperature)')
    
#     # Add regression line for humidity vs stay if valid
#     if not np.isnan(slope_hum):
#         x_line_hum = np.linspace(df['humidity_percent'].min(), df['humidity_percent'].max(), 100)
#         y_line_hum = slope_hum * x_line_hum + intercept_hum
#         plt.plot(x_line_hum, y_line_hum, color='red', linestyle='--', linewidth=2, label='Regression Trend Line')
#         plt.legend()
    
#     plot_path2 = os.path.join(elephant_year_plots, f'{elephant_id}_stays_vs_hum_temp_{year}.png')
#     plt.savefig(plot_path2, dpi=300, bbox_inches='tight')
#     plt.close()
    
#     # Plot 2b: Similar for Humidity (repeat structure for hum_sorted)
#     plt.figure(figsize=(10, 6))
#     hum_sorted = df.sort_values('humidity_percent').copy()
#     if available_months:
#         hum_sorted['month_idx'] = hum_sorted['month'].map({m: i for i, m in enumerate(available_months)})
#         # Plot connection line
#         plt.plot(hum_sorted['humidity_percent'], hum_sorted['stay_duration_hours'], color='gray', linestyle='-', alpha=0.5, linewidth=1, label='Connection Line')
#         # Scatter with available cmap
#         mask_hum = hum_sorted['month'].isin(available_months)
#         if mask_hum.sum() > 0:
#             scatter_month_hum = plt.scatter(hum_sorted.loc[mask_hum, 'humidity_percent'], hum_sorted.loc[mask_hum, 'stay_duration_hours'],
#                                             c=hum_sorted.loc[mask_hum, 'month_idx'], cmap=custom_cmap_avail, alpha=0.7, s=50,
#                                             edgecolors='black', linewidth=0.5)
#             # Colorbar with available months only
#             cbar_hum = plt.colorbar(scatter_month_hum, label='Month', ticks=range(len(available_months)))
#             cbar_hum.set_ticklabels(month_names_avail)
#     plt.xlabel('Humidity (%)')
#     plt.ylabel('Stay Duration (hours)')
#     plt.title(f'{elephant_id} - {year} ({season}): Line Chart - Stay Duration vs Humidity (colored by Month)')
#     plt.grid(True, alpha=0.3)
#     plt.legend()
#     plot_path2b = os.path.join(elephant_year_plots, f'{elephant_id}_line_stays_vs_hum_month_{year}.png')
#     plt.savefig(plot_path2b, dpi=300, bbox_inches='tight')
#     plt.close()
    
#      # Plot 3: Month-wise Correlation Heatmap
#     if available_months:
#         for month in available_months:
#             month_name = month_abbr[month][:3]
#             df_month = df[df['month'] == month].copy()
#             if len(df_month) < 2:  # Need at least 2 rows for corr
#                 print(f"Skipping correlation heatmap for {month_name}: Insufficient data")
#                 continue
#             corr_matrix_month = df_month[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].corr()
#             plt.figure(figsize=(8, 6))
#             sns.heatmap(corr_matrix_month, annot=True, cmap='coolwarm', center=0)
#             plt.title(f'{elephant_id} - {year} - {month_name}: Correlation Heatmap')
#             plot_path3 = os.path.join(elephant_year_plots, f'{elephant_id}_correlation_heatmap_{year}_month_{month}.png')
#             plt.savefig(plot_path3, dpi=300, bbox_inches='tight')
#             plt.close()
#             print(f"Saved month-wise correlation heatmap for {month_name}: {plot_path3}")
    
    
#     plt.figure(figsize=(10, 6))
#     scatter_precip = plt.scatter(df['Precip_mm'], df['stay_duration_hours'], c=df['temp_c'], cmap='coolwarm', alpha=0.6)
#     plt.colorbar(scatter_precip, label='Temperature (°C)')
#     plt.xlabel('Precipitation (mm)')
#     plt.ylabel('Stay Duration (hours)')
#     plt.title(f'{elephant_id} - {year} ({season}): Stay Duration vs Precipitation (colored by Temperature)')
    
#     # Add regression line for precip vs stay if valid
#     if not np.isnan(slope_precip):
#         x_line_precip = np.linspace(df['Precip_mm'].min(), df['Precip_mm'].max(), 100)
#         y_line_precip = slope_precip * x_line_precip + intercept_precip
#         plt.plot(x_line_precip, y_line_precip, color='red', linestyle='--', linewidth=2, label='Regression Trend Line')
#         plt.legend()
    
#     plot_path3 = os.path.join(elephant_year_plots, f'{elephant_id}_stays_vs_precip_temp_{year}.png')
#     plt.savefig(plot_path3, dpi=300, bbox_inches='tight')
#     plt.close()
    
#     # New Plot 4: Scatter Stay vs Precip, colored by Humidity
#     plt.figure(figsize=(10, 6))
#     scatter_precip_hum = plt.scatter(df['Precip_mm'], df['stay_duration_hours'], c=df['humidity_percent'], cmap='viridis', alpha=0.6)
#     plt.colorbar(scatter_precip_hum, label='Humidity %')
#     plt.xlabel('Precipitation (mm)')
#     plt.ylabel('Stay Duration (hours)')
#     plt.title(f'{elephant_id} - {year} ({season}): Stay Duration vs Precipitation (colored by Humidity)')
    
#     # Add regression line if valid
#     if not np.isnan(slope_precip):
#         plt.plot(x_line_precip, y_line_precip, color='red', linestyle='--', linewidth=2, label='Regression Trend Line')
#         plt.legend()
    
#     plot_path4 = os.path.join(elephant_year_plots, f'{elephant_id}_stays_vs_precip_hum_{year}.png')
#     plt.savefig(plot_path4, dpi=300, bbox_inches='tight')
#     plt.close()
    
#     # New Plot 5: Scatter Stay vs Precip, colored by Month (using available colors)
#     if available_months:
#         plt.figure(figsize=(10, 6))
#         precip_sorted = df.sort_values('Precip_mm').copy()
#         precip_sorted['month_idx'] = precip_sorted['month'].map({m: i for i, m in enumerate(available_months)})
#         # Plot connection line
#         plt.plot(precip_sorted['Precip_mm'], precip_sorted['stay_duration_hours'], color='gray', linestyle='-', alpha=0.5, linewidth=1, label='Connection Line')
#         # Scatter with available cmap
#         mask_precip = precip_sorted['month'].isin(available_months)
#         if mask_precip.sum() > 0:
#             scatter_precip_month = plt.scatter(precip_sorted.loc[mask_precip, 'Precip_mm'], precip_sorted.loc[mask_precip, 'stay_duration_hours'],
#                                                c=precip_sorted.loc[mask_precip, 'month_idx'], cmap=custom_cmap_avail, alpha=0.7, s=50,
#                                                edgecolors='black', linewidth=0.5)
#             # Colorbar with available months
#             cbar_precip = plt.colorbar(scatter_precip_month, label='Month', ticks=range(len(available_months)))
#             cbar_precip.set_ticklabels(month_names_avail)
#         plt.xlabel('Precipitation (mm)')
#         plt.ylabel('Stay Duration (hours)')
#         plt.title(f'{elephant_id} - {year} ({season}): Line Chart - Stay Duration vs Precipitation (colored by Month)')
#         plt.grid(True, alpha=0.3)
#         plt.legend()
#         plot_path5 = os.path.join(elephant_year_plots, f'{elephant_id}_line_stays_vs_precip_month_{year}.png')
#         plt.savefig(plot_path5, dpi=300, bbox_inches='tight')
#         plt.close()
#     # New Plot 7: Month-wise Heatmap of High Stay Proportion by Temp and Hum/Precip Categories (fixed labeling and reindex)
#     if available_months:
#         for month in available_months:
#             month_name = month_abbr[month][:3]
#             df_month = df[df['month'] == month].copy()
#             if len(df_month) == 0:
#                 print(f"Skipping heatmap for {month_name}: No data")
#                 continue
#             # Recompute categories for this month (using month's quantiles for bins)
#             df_month['temp_cat'] = pd.cut(df_month['temp_c'], bins=3, labels=['Low', 'Med', 'High'])
#             df_month['hum_cat'] = pd.cut(df_month['humidity_percent'], bins=3, labels=['Low', 'Med', 'High'])
#             df_month['precip_cat'] = pd.cut(df_month['Precip_mm'], bins=3, labels=['Low', 'Med', 'High'])
#             month_stay_high_thresh = df_month['stay_duration_hours'].median()
#             df_month['stay_cat'] = np.where(df_month['stay_duration_hours'] > month_stay_high_thresh, 'High', 'Low')
#             df_month['hum_precip_combined'] = df_month['hum_cat'].astype(str) + '-' + df_month['precip_cat'].astype(str)
            
#             crosstab_stay = pd.crosstab([df_month['temp_cat'], df_month['hum_precip_combined']], df_month['stay_cat'], normalize='index')  # Proportions
#             # Safely get 'High' column, default to zeros if missing
#             high_stay_series = crosstab_stay.get('High', pd.Series(0, index=crosstab_stay.index))
#             high_stay_prop = high_stay_series.unstack(fill_value=0)
#             # Convert index to regular strings to avoid CategoricalIndex issues
#             high_stay_prop.index = high_stay_prop.index.astype(str)
#             high_stay_prop.columns = high_stay_prop.columns.astype(str)
#             # Reindex to ensure all temp_cat and combined categories are present (no 'level' arg)
#             all_temp_cats = ['Low', 'Med', 'High']
#             all_hum_precip_combos = sorted(df_month['hum_precip_combined'].unique())
#             high_stay_prop = high_stay_prop.reindex(index=all_temp_cats, columns=all_hum_precip_combos, fill_value=0)
#             # Create the heatmap with explicit row labels for temp_cat
#             plt.figure(figsize=(12, 8))  # Larger for combined labels
#             sns.heatmap(high_stay_prop, annot=True, fmt='.2f', cmap='YlOrRd', cbar_kws={'label': 'Proportion of High Stay'})
#             # Explicitly set y-axis labels to temp_cat only (Low, Med, High)
#             plt.yticks(ticks=np.arange(len(all_temp_cats)) + 0.5, labels=all_temp_cats, rotation=0)
#             plt.title(f'{elephant_id} - {year} - {month_name}: Proportion of High Stay by Temperature Categories (Hum-Precip Combined)')
#             plt.xlabel('Humidity-Precipitation Category (e.g., Low-Low)')
#             plt.ylabel('Temperature Category')
#             plt.xticks(rotation=45, ha='right')
#             plot_path7 = os.path.join(elephant_year_plots, f'{elephant_id}_high_stay_prop_heatmap_{year}_month_{month}.png')
#             plt.savefig(plot_path7, dpi=300, bbox_inches='tight')
#             plt.close()
#             print(f"Saved month-wise heatmap for {month_name}: {plot_path7}")
#     # New Plot 8: Grouped Bar Chart - Count of Stay Cat by Temp Cat (faceted by Hum Cat) - now with precip
#     plt.figure(figsize=(12, 6))
#     crosstab_temp_stay = pd.crosstab([df['temp_cat'], df['hum_cat'], df['precip_cat']], df['stay_cat'])
#     # Ensure columns exist, add zeros if missing
#     if 'High' not in crosstab_temp_stay.columns:
#         crosstab_temp_stay['High'] = 0
#     if 'Low' not in crosstab_temp_stay.columns:
#         crosstab_temp_stay['Low'] = 0
#     crosstab_temp_stay.unstack().plot(kind='bar', stacked=True, figsize=(12, 6))
#     plt.title(f'{elephant_id} - {year} ({season}): Stay Categories by Temp (Grouped by Hum/Precip)')
#     plt.xlabel('Temperature Category')
#     plt.ylabel('Count')
#     plt.legend(title='Stay Category')
#     plt.xticks(rotation=45)
#     plot_path8 = os.path.join(elephant_year_plots, f'{elephant_id}_stay_by_temp_hum_precip_grouped_{year}.png')
#     plt.savefig(plot_path8, dpi=300, bbox_inches='tight')
#     plt.close()
#     # New Plot 9: 3D Bar-like visualization using grouped bars for all three (now with precip)
#     fig, ax = plt.subplots(figsize=(10, 7))
#     temp_cats = df['temp_cat'].cat.categories
#     hum_cats = df['hum_cat'].cat.categories  # Use hum_cats for faceting, precip in condition
#     width = 0.25
#     x = np.arange(len(temp_cats))
#     for i, hum in enumerate(hum_cats):
#         subset = df[df['hum_cat'] == hum]
#         crosstab_subset = pd.crosstab(subset['temp_cat'], subset['stay_cat'])
        
#         # Safely get 'High' column, default to zeros if missing
#         high_series = crosstab_subset.get('High', pd.Series(0, index=temp_cats))
#         high_counts = high_series.reindex(temp_cats, fill_value=0)
        
#         # Safely get 'Low' column, default to zeros if missing
#         low_series = crosstab_subset.get('Low', pd.Series(0, index=temp_cats))
#         low_counts = low_series.reindex(temp_cats, fill_value=0)
        
#         # Plot bars
#         ax.bar(x + i*width, high_counts, width, label=f'High Stay - {hum}', alpha=0.8)
#         ax.bar(x + i*width + width, low_counts, width, label=f'Low Stay - {hum}', alpha=0.8, bottom=high_counts)
#     ax.set_xlabel('Temperature Category')
#     ax.set_ylabel('Count')
#     ax.set_title(f'{elephant_id} - {year} ({season}): Stay Counts by Temp, Faceted by Hum (Precip in Condition)')
#     ax.set_xticks(x + width)
#     ax.set_xticklabels(temp_cats)
#     ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
#     plt.tight_layout()
#     plot_path9 = os.path.join(elephant_year_plots, f'{elephant_id}_3way_stay_temp_hum_precip_{year}.png')
#     plt.savefig(plot_path9, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Added 3-category plots saved to: {elephant_year_plots}")
    
#     # Debug: Check if a plot file exists
#     if os.path.exists(plot_path1):
#         print(f"Confirmed: Example plot exists at {plot_path1}")
#     else:
#         print(f"Error: Plot not saved at {plot_path1}")
    
#     print(f"Plots saved to: {elephant_year_plots}")

# print(f"\nAll per-elephant-year analyses completed. Enhanced CSVs and plots in: {analysis_dir}")
# print("Enhanced CSVs include 'stay_cat' (High/Low based on median stay duration) and other categories.")
# # Final debug: List contents of analysis_dir
# print(f"\nContents of {analysis_dir}:")
# if os.path.exists(analysis_dir):
#     contents = os.listdir(analysis_dir)
#     for item in contents:
#         item_path = os.path.join(analysis_dir, item)
#         if os.path.isdir(item_path):
#             print(f"  [DIR] {item}")
#         else:
#             print(f"  [FILE] {item}")
# else:
#     print("Analysis directory does not exist!")

# import pandas as pd
# import glob
# import numpy as np
# import os
# import matplotlib.pyplot as plt
# import matplotlib.colors as mcolors
# from calendar import month_abbr # For month names
# import seaborn as sns
# from scipy import stats
# from datetime import datetime
# # Define paths (using your exact full paths) - Ensure no extra spaces or typos
# old_plots_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_StayDuration\analysis1'
# new_save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_StayDuration'
# analysis_dir = os.path.join(new_save_path, 'stay_analysis1')
# weather_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\okaukuejo_weather_all_years.csv' # Add weather path
# # Debug: Print and normalize paths
# print(f"Working directory: {os.getcwd()}")
# print(f"Loading stays from: {old_plots_dir}")
# print(f"Raw analysis_dir: {analysis_dir}")
# # Normalize path to handle any Windows quirks
# analysis_dir = os.path.normpath(analysis_dir)
# print(f"Normalized analysis_dir: {analysis_dir}")
# # Step-by-step path verification
# parent_dir = os.path.dirname(analysis_dir)
# print(f"Parent directory: {parent_dir}")
# print(f"Parent exists: {os.path.exists(parent_dir)}")
# # Load weather data once (outside loop)
# try:
#     weather = pd.read_csv(weather_path, encoding='utf-8')
# except UnicodeDecodeError:
#     weather = pd.read_csv(weather_path, encoding='latin-1')
# weather['date'] = pd.to_datetime(weather['Date']).dt.date
# precip_dict = dict(zip(weather['date'], weather['Precip_mm']))
# # Load all daily waterhole stays CSVs from old directory and process per elephant-year
# stay_files = glob.glob(os.path.join(old_plots_dir, '*_daily_waterhole_stays.csv'))
# print(f"Found {len(stay_files)} stay files in {old_plots_dir}")
# if not stay_files:
#     print("No stay CSV files found in:", old_plots_dir)
#     exit()
# # Create analysis directory step by step
# os.makedirs(new_save_path, exist_ok=True)
# print(f"Created/verified base save path: {new_save_path}")
# os.makedirs(analysis_dir, exist_ok=True)
# print(f"Created/verified analysis_dir: {analysis_dir}")
# for f in stay_files:
#     # Load per elephant-year CSV
#     df = pd.read_csv(f)
#     # Improved filename parsing for stays file: {elephant_id}_{year}_daily_waterhole_stays.csv
#     filename_base = os.path.basename(f).replace('.csv', '')
#     parts = filename_base.split('_')
#     elephant_id = parts[0]
#     year = parts[1] # Second part is year (before 'daily...')
#     print(f"\nProcessing {elephant_id} - {year} (from file: {filename_base})")
   
#     # Use existing 'season' column from the loaded stays CSV (already populated from original data)
#     # Assume it's uniform per elephant-year; take the first non-null value
#     if 'season' in df.columns and not df['season'].isna().all():
#         season = df['season'].dropna().iloc[0] # Use first non-null
#         print(f" Using season from stays data: {season}")
#     else:
#         season = 'unknown'
#         print(f" Warning: No valid season in stays data; using 'unknown'")
   
#     # Map Precip_mm from weather by date
#     df['date'] = pd.to_datetime(df['date']).dt.date # Ensure date column is date type
#     df['Precip_mm'] = df['date'].map(precip_dict)
   
#     # Drop rows with missing Precip_mm
#     df = df.dropna(subset=['Precip_mm'])
   
#     # Parse start_time_str to extract hour
#     df['start_hour'] = pd.to_datetime(df['start_time_str']).dt.hour
   
#     # Basic statistics (now including Precip_mm and season)
#     print("\nBasic Statistics:")
#     stats_desc = df[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].describe()
#     print(stats_desc)
   
#     # Correlations (now including Precip_mm)
#     corr_matrix = df[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].corr()
#     print("\nCorrelation Matrix:")
#     print(corr_matrix)
   
#     # Linear regression (now including Precip_mm, with check for identical values)
#     if len(df) > 1:
#         slope_temp, intercept_temp, r_temp, p_temp, std_err_temp = stats.linregress(df['temp_c'], df['stay_duration_hours'])
#         slope_hum, intercept_hum, r_hum, p_hum, std_err_hum = stats.linregress(df['humidity_percent'], df['stay_duration_hours'])
       
#         print(f"\nLinear Regression Results:")
#         print(f"Stay Duration ~ Temp_C: slope={slope_temp:.4f}, r={r_temp:.4f}, p={p_temp:.4f}")
#         print(f"Stay Duration ~ Humidity_%: slope={slope_hum:.4f}, r={r_hum:.4f}, p={p_hum:.4f}")
       
#         # Check for Precip_mm regression - skip if all values identical (variance=0)
#         if df['Precip_mm'].std() > 0 and df['Precip_mm'].nunique() > 1:
#             slope_precip, intercept_precip, r_precip, p_precip, std_err_precip = stats.linregress(df['Precip_mm'], df['stay_duration_hours'])
#             print(f"Stay Duration ~ Precip_mm: slope={slope_precip:.4f}, r={r_precip:.4f}, p={p_precip:.4f}")
#         else:
#             print("Skipping Precip regression: all Precip_mm values are identical (likely 0 mm in dry season).")
#             slope_precip, intercept_precip, r_precip, p_precip, std_err_precip = np.nan, np.nan, np.nan, np.nan, np.nan # Set to NaN for plotting
#     else:
#         print("\nInsufficient data for regression.")
#         slope_temp, intercept_temp, r_temp, p_temp = np.nan, np.nan, np.nan, np.nan
#         slope_hum, intercept_hum, r_hum, p_hum = np.nan, np.nan, np.nan, np.nan
#         slope_precip, intercept_precip, r_precip, p_precip = np.nan, np.nan, np.nan, np.nan
   
#     # Define thresholds (per elephant-year) - now including precip
#     temp_high_thresh = df['temp_c'].quantile(0.75)
#     hum_low_thresh = df['humidity_percent'].quantile(0.25)
#     precip_high_thresh = df['Precip_mm'].quantile(0.75) # High precip threshold
#     stay_high_thresh = df['stay_duration_hours'].median() # High stay as above median
   
#     print(f"\nHigh Temp Threshold (> {temp_high_thresh:.1f}°C), Low Humidity Threshold (< {hum_low_thresh:.1f}%)")
#     print(f"High Precip Threshold (> {precip_high_thresh:.1f} mm)")
#     print(f"High Stay Threshold (> {stay_high_thresh:.2f} hours)")
   
#     # Overall average stay
#     avg_stay_all = df['stay_duration_hours'].mean()
#     print(f"Average stay duration overall: {avg_stay_all:.2f} hours")
   
#     # Filter for high temp low humidity (keep as is, or add precip filter if needed)
#     high_temp_low_hum = df[(df['temp_c'] > temp_high_thresh) & (df['humidity_percent'] < hum_low_thresh)]
#     if len(high_temp_low_hum) > 0:
#         avg_stay_high_low = high_temp_low_hum['stay_duration_hours'].mean()
#         print(f"Average stay duration under high temp & low humidity: {avg_stay_high_low:.2f} hours")
#         print(f"Number of such stays: {len(high_temp_low_hum)}")
       
#         # Start hour distribution
#         hour_dist = high_temp_low_hum['start_hour'].value_counts().sort_index()
#         print("\nStart hour distribution under high temp & low humidity:")
#         print(hour_dist)
       
#         # Overall start hour distribution
#         hour_dist_all = df['start_hour'].value_counts().sort_index()
#         print("\nStart hour distribution overall:")
#         print(hour_dist_all)
#     else:
#         print("No stays found under high temp & low humidity conditions.")
   
#     # Add categorical columns (now including precip_cat)
#     df['temp_cat'] = pd.cut(df['temp_c'], bins=3, labels=['Low', 'Med', 'High'])
#     df['hum_cat'] = pd.cut(df['humidity_percent'], bins=3, labels=['Low', 'Med', 'High'])
#     df['precip_cat'] = pd.cut(df['Precip_mm'], bins=3, labels=['Low', 'Med', 'High'])
#     df['stay_cat'] = np.where(df['stay_duration_hours'] > stay_high_thresh, 'High', 'Low')
#     df['condition'] = df['temp_cat'].astype(str) + ' Temp + ' + df['hum_cat'].astype(str) + ' Hum + ' + df['precip_cat'].astype(str) + ' Precip'
   
#     # Save enhanced CSV with renamed format including year (now with Precip_mm and season)
#     enhanced_csv_path = os.path.join(analysis_dir, f'{elephant_id}_stays_enhanced_stays_{year}.csv')
#     enhanced_cols = ['elephant_id', 'year', 'date', 'waterhole', 'lon', 'lat', 'start_time_str', 'end_time_str', 'stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm', 'start_hour', 'temp_cat', 'hum_cat', 'precip_cat', 'stay_cat', 'condition', 'season']
#     df[enhanced_cols].to_csv(enhanced_csv_path, index=False)
#     print(f"Saved enhanced CSV: {enhanced_csv_path}")
   
#     # Debug: Check if file exists and its size
#     if os.path.exists(enhanced_csv_path):
#         file_size = os.path.getsize(enhanced_csv_path)
#         print(f"✓ Confirmed: CSV exists at {enhanced_csv_path} (size: {file_size} bytes)")
#     else:
#         print(f"✗ Error: CSV not saved at {enhanced_csv_path}")
#         # Try alternative save with full path
#         try:
#             df[enhanced_cols].to_csv(enhanced_csv_path, index=False)
#             print(f"Retry successful: {enhanced_csv_path}")
#         except Exception as e:
#             print(f"Save error: {e}")
   
#     # Create per elephant-year plots directory with renamed format including year
#     elephant_year_plots = os.path.join(analysis_dir, f'{elephant_id}_stays_{year}')
#     os.makedirs(elephant_year_plots, exist_ok=True)
#     print(f"Created/verified plots dir: {elephant_year_plots}")
   
#     # Define 12 custom colors for months 1-12
#     month_colors_full = [
#         '#1E90FF', '#FF4500', '#32CD32', '#8A2BE2', '#FFD700', '#FFA500',
#         '#A9A9A9', '#00CED1', '#FF69B4', '#8B4513', '#008080', '#FF00FF'
#     ]
   
#     # Ensure month column is added (do this once per file)
#     df['date_dt'] = pd.to_datetime(df['date'])
#     df['month'] = df['date_dt'].dt.month
   
#     # Get available months only
#     available_months = sorted(df['month'].dropna().unique())
#     if not available_months:
#         print("No valid months found; skipping month-colored plots.")
#         # Continue to other plots...
#     else:
#         # Month names for available months
#         month_names_avail = [month_abbr[m][:3] for m in available_months]
       
#         # Custom colors (full 12, but slice for available)
#         month_colors_avail = [month_colors_full[m-1] for m in available_months]
#         custom_cmap_avail = mcolors.ListedColormap(month_colors_avail)
       
#         print(f"Available months: {month_names_avail}")
#         print(f"Corresponding colors: {month_colors_avail}")
#      # Plot 3: Month-wise Correlation Heatmap
#     if available_months:
#         for month in available_months:
#             month_name = month_abbr[month][:3]
#             df_month = df[df['month'] == month].copy()
#             if len(df_month) < 2: # Need at least 2 rows for corr
#                 print(f"Skipping correlation heatmap for {month_name}: Insufficient data")
#                 continue
#             corr_matrix_month = df_month[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].corr()
#             plt.figure(figsize=(8, 6))
#             sns.heatmap(corr_matrix_month, annot=True, cmap='coolwarm', center=0)
#             plt.title(f'{elephant_id} - {year} - {month_name}: Correlation Heatmap')
#             plot_path3 = os.path.join(elephant_year_plots, f'{elephant_id}_correlation_heatmap_{year}_month_{month}.png')
#             plt.savefig(plot_path3, dpi=300, bbox_inches='tight')
#             plt.close()
#             print(f"Saved month-wise correlation heatmap for {month_name}: {plot_path3}")
#     # New Plot 7: Month-wise Heatmap of High Stay Proportion by Temp and Hum/Precip Categories (fixed labeling and reindex)
#     if available_months:
#         for month in available_months:
#             month_name = month_abbr[month][:3]
#             df_month = df[df['month'] == month].copy()
#             if len(df_month) == 0:
#                 print(f"Skipping heatmap for {month_name}: No data")
#                 continue
#             # Recompute categories for this month (using month's quantiles for bins)
#             df_month['temp_cat'] = pd.cut(df_month['temp_c'], bins=3, labels=['Low', 'Med', 'High'])
#             df_month['hum_cat'] = pd.cut(df_month['humidity_percent'], bins=3, labels=['Low', 'Med', 'High'])
#             df_month['precip_cat'] = pd.cut(df_month['Precip_mm'], bins=3, labels=['Low', 'Med', 'High'])
#             month_stay_high_thresh = df_month['stay_duration_hours'].median()
#             df_month['stay_cat'] = np.where(df_month['stay_duration_hours'] > month_stay_high_thresh, 'High', 'Low')
#             df_month['hum_precip_combined'] = df_month['hum_cat'].astype(str) + '-' + df_month['precip_cat'].astype(str)
           
#             crosstab_stay = pd.crosstab([df_month['temp_cat'], df_month['hum_precip_combined']], df_month['stay_cat'], normalize='index') # Proportions
#             # Safely get 'High' column, default to zeros if missing
#             high_stay_series = crosstab_stay.get('High', pd.Series(0, index=crosstab_stay.index))
#             high_stay_prop = high_stay_series.unstack(fill_value=0)
#             # Convert index to regular strings to avoid CategoricalIndex issues
#             high_stay_prop.index = high_stay_prop.index.astype(str)
#             high_stay_prop.columns = high_stay_prop.columns.astype(str)
#             # Reindex to ensure all temp_cat and combined categories are present (no 'level' arg)
#             all_temp_cats = ['Low', 'Med', 'High']
#             all_hum_precip_combos = sorted(df_month['hum_precip_combined'].unique())
#             high_stay_prop = high_stay_prop.reindex(index=all_temp_cats, columns=all_hum_precip_combos, fill_value=0)
#             # Create the heatmap with explicit row labels for temp_cat
#             plt.figure(figsize=(12, 8)) # Larger for combined labels
#             sns.heatmap(high_stay_prop, annot=True, fmt='.2f', cmap='YlOrRd', cbar_kws={'label': 'Proportion of High Stay'})
#             # Explicitly set y-axis labels to temp_cat only (Low, Med, High)
#             plt.yticks(ticks=np.arange(len(all_temp_cats)) + 0.5, labels=all_temp_cats, rotation=0)
#             plt.title(f'{elephant_id} - {year} - {month_name}: Proportion of High Stay by Temperature Categories (Hum-Precip Combined)')
#             plt.xlabel('Humidity-Precipitation Category (e.g., Low-Low)')
#             plt.ylabel('Temperature Category')
#             plt.xticks(rotation=45, ha='right')
#             plot_path7 = os.path.join(elephant_year_plots, f'{elephant_id}_high_stay_prop_heatmap_{year}_month_{month}.png')
#             plt.savefig(plot_path7, dpi=300, bbox_inches='tight')
#             plt.close()
#             print(f"Saved month-wise heatmap for {month_name}: {plot_path7}")
# print(f"\nAll per-elephant-year analyses completed. Enhanced CSVs and plots in: {analysis_dir}")
# print("Enhanced CSVs include 'stay_cat' (High/Low based on median stay duration) and other categories.")
# # Final debug: List contents of analysis_dir
# print(f"\nContents of {analysis_dir}:")
# if os.path.exists(analysis_dir):
#     contents = os.listdir(analysis_dir)
#     for item in contents:
#         item_path = os.path.join(analysis_dir, item)
#         if os.path.isdir(item_path):
#             print(f" [DIR] {item}")
#         else:
#             print(f" [FILE] {item}")
# else:
#     print("Analysis directory does not exist!")

import pandas as pd
import glob
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from calendar import month_abbr  # For month names
import seaborn as sns
from scipy import stats
from datetime import datetime
import re  # Added for robust filename parsing

# Define paths (using your exact full paths) - Ensure no extra spaces or typos
old_plots_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_StayDuration\analysis1'
new_save_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\Waterhole_StayDuration'
analysis_dir = os.path.join(new_save_path, 'stay_analysis1')
weather_path = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\okaukuejo_weather_all_years.csv'  # Add weather path

# Debug: Print and normalize paths
print(f"Working directory: {os.getcwd()}")
print(f"Loading stays from: {old_plots_dir}")
print(f"Raw analysis_dir: {analysis_dir}")
# Normalize path to handle any Windows quirks
analysis_dir = os.path.normpath(analysis_dir)
print(f"Normalized analysis_dir: {analysis_dir}")
# Step-by-step path verification
parent_dir = os.path.dirname(analysis_dir)
print(f"Parent directory: {parent_dir}")
print(f"Parent exists: {os.path.exists(parent_dir)}")

# Load weather data once (outside loop)
try:
    weather = pd.read_csv(weather_path, encoding='utf-8')
except UnicodeDecodeError:
    weather = pd.read_csv(weather_path, encoding='latin-1')
weather['date'] = pd.to_datetime(weather['Date']).dt.date
precip_dict = dict(zip(weather['date'], weather['Precip_mm']))

# Load all daily waterhole stays CSVs from old directory and process per elephant-year
stay_files = glob.glob(os.path.join(old_plots_dir, '*_daily_waterhole_stays.csv'))
print(f"Found {len(stay_files)} stay files in {old_plots_dir}")
if not stay_files:
    print("No stay CSV files found in:", old_plots_dir)
    exit()

# Create analysis directory step by step
os.makedirs(new_save_path, exist_ok=True)
print(f"Created/verified base save path: {new_save_path}")
os.makedirs(analysis_dir, exist_ok=True)
print(f"Created/verified analysis_dir: {analysis_dir}")

for f in stay_files:
    # Load per elephant-year CSV
    df = pd.read_csv(f)
    # Improved filename parsing for stays file: {elephant_id}_{year}_daily_waterhole_stays.csv (using _ not *)
    filename_base = os.path.basename(f).replace('.csv', '')
    print(f"Debug: Processing file basename: {filename_base}")  # Added debug print
    
    # Use regex for robust parsing - adjusted for _ separators
    match = re.match(r'^(\w+)_(\d{4})_daily_waterhole_stays$', filename_base)
    if match:
        elephant_id = match.group(1)
        year = match.group(2)
        print(f"✓ Parsed: elephant_id={elephant_id}, year={year}")
    else:
        print(f"✗ Skipping file {filename_base}: Filename does not match expected pattern '{example_pattern}' where example_pattern is like '01fe_2010_daily_waterhole_stays'")
        continue  # Skip this file and move to next
    
    print(f"\nProcessing {elephant_id} - {year} (from file: {filename_base})")
    
    # Use existing 'season' column from the loaded stays CSV (already populated from original data)
    # Assume it's uniform per elephant-year; take the first non-null value
    if 'season' in df.columns and not df['season'].isna().all():
        season = df['season'].dropna().iloc[0]  # Use first non-null
        print(f" Using season from stays data: {season}")
    else:
        season = 'unknown'
        print(f" Warning: No valid season in stays data; using 'unknown'")
    
    # Map Precip_mm from weather by date
    df['date'] = pd.to_datetime(df['date']).dt.date  # Ensure date column is date type
    df['Precip_mm'] = df['date'].map(precip_dict)
    
    # Drop rows with missing Precip_mm
    df = df.dropna(subset=['Precip_mm'])
    
    # Parse start_time_str to extract hour
    df['start_hour'] = pd.to_datetime(df['start_time_str']).dt.hour
    
    # Basic statistics (now including Precip_mm and season)
    print("\nBasic Statistics:")
    stats_desc = df[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].describe()
    print(stats_desc)
    
    # Correlations (now including Precip_mm)
    corr_matrix = df[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].corr()
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    # Linear regression (now including Precip_mm, with check for identical values)
    if len(df) > 1:
        slope_temp, intercept_temp, r_temp, p_temp, std_err_temp = stats.linregress(df['temp_c'], df['stay_duration_hours'])
        slope_hum, intercept_hum, r_hum, p_hum, std_err_hum = stats.linregress(df['humidity_percent'], df['stay_duration_hours'])
        
        print(f"\nLinear Regression Results:")
        print(f"Stay Duration ~ Temp_C: slope={slope_temp:.4f}, r={r_temp:.4f}, p={p_temp:.4f}")
        print(f"Stay Duration ~ Humidity*%: slope={slope_hum:.4f}, r={r_hum:.4f}, p={p_hum:.4f}")
        
        # Check for Precip_mm regression - skip if all values identical (variance=0)
        if df['Precip_mm'].std() > 0 and df['Precip_mm'].nunique() > 1:
            slope_precip, intercept_precip, r_precip, p_precip, std_err_precip = stats.linregress(df['Precip_mm'], df['stay_duration_hours'])
            print(f"Stay Duration ~ Precip_mm: slope={slope_precip:.4f}, r={r_precip:.4f}, p={p_precip:.4f}")
        else:
            print("Skipping Precip regression: all Precip_mm values are identical (likely 0 mm in dry season).")
            slope_precip, intercept_precip, r_precip, p_precip, std_err_precip = np.nan, np.nan, np.nan, np.nan, np.nan  # Set to NaN for plotting
    else:
        print("\nInsufficient data for regression.")
        slope_temp, intercept_temp, r_temp, p_temp = np.nan, np.nan, np.nan, np.nan
        slope_hum, intercept_hum, r_hum, p_hum = np.nan, np.nan, np.nan, np.nan
        slope_precip, intercept_precip, r_precip, p_precip = np.nan, np.nan, np.nan, np.nan
    
    # Define thresholds (per elephant-year) - now including precip
    temp_high_thresh = df['temp_c'].quantile(0.75)
    hum_low_thresh = df['humidity_percent'].quantile(0.25)
    precip_high_thresh = df['Precip_mm'].quantile(0.75)  # High precip threshold
    stay_high_thresh = df['stay_duration_hours'].median()  # High stay as above median
    
    print(f"\nHigh Temp Threshold (> {temp_high_thresh:.1f}°C), Low Humidity Threshold (< {hum_low_thresh:.1f}%)")
    print(f"High Precip Threshold (> {precip_high_thresh:.1f} mm)")
    print(f"High Stay Threshold (> {stay_high_thresh:.2f} hours)")
    
    # Overall average stay
    avg_stay_all = df['stay_duration_hours'].mean()
    print(f"Average stay duration overall: {avg_stay_all:.2f} hours")
    
    # Filter for high temp low humidity (keep as is, or add precip filter if needed)
    high_temp_low_hum = df[(df['temp_c'] > temp_high_thresh) & (df['humidity_percent'] < hum_low_thresh)]
    if len(high_temp_low_hum) > 0:
        avg_stay_high_low = high_temp_low_hum['stay_duration_hours'].mean()
        print(f"Average stay duration under high temp & low humidity: {avg_stay_high_low:.2f} hours")
        print(f"Number of such stays: {len(high_temp_low_hum)}")
        
        # Start hour distribution
        hour_dist = high_temp_low_hum['start_hour'].value_counts().sort_index()
        print("\nStart hour distribution under high temp & low humidity:")
        print(hour_dist)
        
        # Overall start hour distribution
        hour_dist_all = df['start_hour'].value_counts().sort_index()
        print("\nStart hour distribution overall:")
        print(hour_dist_all)
    else:
        print("No stays found under high temp & low humidity conditions.")
    
    # Add categorical columns (now including precip_cat)
    df['temp_cat'] = pd.cut(df['temp_c'], bins=3, labels=['Low', 'Med', 'High'])
    df['hum_cat'] = pd.cut(df['humidity_percent'], bins=3, labels=['Low', 'Med', 'High'])
    df['precip_cat'] = pd.cut(df['Precip_mm'], bins=3, labels=['Low', 'Med', 'High'])
    df['stay_cat'] = np.where(df['stay_duration_hours'] > stay_high_thresh, 'High', 'Low')
    df['condition'] = df['temp_cat'].astype(str) + ' Temp + ' + df['hum_cat'].astype(str) + ' Hum + ' + df['precip_cat'].astype(str) + ' Precip'
    
    # Save enhanced CSV with renamed format including year (now with Precip_mm and season) - using _ for consistency
    enhanced_csv_path = os.path.join(analysis_dir, f'{elephant_id}_stays_enhanced_stays_{year}.csv')
    enhanced_cols = ['elephant_id', 'year', 'date', 'waterhole', 'lon', 'lat', 'start_time_str', 'end_time_str', 'stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm', 'start_hour', 'temp_cat', 'hum_cat', 'precip_cat', 'stay_cat', 'condition', 'season']
    df[enhanced_cols].to_csv(enhanced_csv_path, index=False)
    print(f"Saved enhanced CSV: {enhanced_csv_path}")
    
    # Debug: Check if file exists and its size
    if os.path.exists(enhanced_csv_path):
        file_size = os.path.getsize(enhanced_csv_path)
        print(f"✓ Confirmed: CSV exists at {enhanced_csv_path} (size: {file_size} bytes)")
    else:
        print(f"✗ Error: CSV not saved at {enhanced_csv_path}")
        # Try alternative save with full path
        try:
            df[enhanced_cols].to_csv(enhanced_csv_path, index=False)
            print(f"Retry successful: {enhanced_csv_path}")
        except Exception as e:
            print(f"Save error: {e}")
    
    # Create per elephant-year plots directory with renamed format including year - using _ 
    elephant_year_plots = os.path.join(analysis_dir, f'{elephant_id}_stays_{year}')
    os.makedirs(elephant_year_plots, exist_ok=True)
    print(f"Created/verified plots dir: {elephant_year_plots}")
    
    # Define 12 custom colors for months 1-12
    month_colors_full = [
        '#1E90FF', '#FF4500', '#32CD32', '#8A2BE2', '#FFD700', '#FFA500',
        '#A9A9A9', '#00CED1', '#FF69B4', '#8B4513', '#008080', '#FF00FF'
    ]
    
    # Ensure month column is added (do this once per file)
    df['date_dt'] = pd.to_datetime(df['date'])
    df['month'] = df['date_dt'].dt.month
    
    # Get available months only
    available_months = sorted(df['month'].dropna().unique())
    if not available_months:
        print("No valid months found; skipping month-colored plots.")
        # Continue to other plots...
    else:
        # Month names for available months
        month_names_avail = [month_abbr[m][:3] for m in available_months]
        
        # Custom colors (full 12, but slice for available)
        month_colors_avail = [month_colors_full[m-1] for m in available_months]
        custom_cmap_avail = mcolors.ListedColormap(month_colors_avail)
        
        print(f"Available months: {month_names_avail}")
        print(f"Corresponding colors: {month_colors_avail}")
    
    # Plot 3: Month-wise Correlation Heatmap
    if available_months:
        for month in available_months:
            month_name = month_abbr[month][:3]
            df_month = df[df['month'] == month].copy()
            if len(df_month) < 2:  # Need at least 2 rows for corr
                print(f"Skipping correlation heatmap for {month_name}: Insufficient data")
                continue
            corr_matrix_month = df_month[['stay_duration_hours', 'temp_c', 'humidity_percent', 'Precip_mm']].corr()
            plt.figure(figsize=(8, 6))
            sns.heatmap(corr_matrix_month, annot=True, cmap='coolwarm', center=0)
            plt.title(f'{elephant_id} - {year} - {month_name}: Correlation Heatmap')
            plot_path3 = os.path.join(elephant_year_plots, f'{elephant_id}_correlation_heatmap_{year}_month_{month}.png')
            plt.savefig(plot_path3, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved month-wise correlation heatmap for {month_name}: {plot_path3}")
    
    # New Plot 7: Yearly Heatmap of High Stay Proportion by Temp and Hum/Precip Categories
    if len(df) > 0:
        # Use existing categories (computed with yearly quantiles) and stay_high_thresh
        df_yearly = df.copy()
        df_yearly['hum_precip_combined'] = df_yearly['hum_cat'].astype(str) + '-' + df_yearly['precip_cat'].astype(str)
        
        crosstab_stay = pd.crosstab([df_yearly['temp_cat'], df_yearly['hum_precip_combined']], df_yearly['stay_cat'], normalize='index')  # Proportions
        # Safely get 'High' column, default to zeros if missing
        high_stay_series = crosstab_stay.get('High', pd.Series(0, index=crosstab_stay.index))
        high_stay_prop = high_stay_series.unstack(fill_value=0)
        # Convert index to regular strings to avoid CategoricalIndex issues
        high_stay_prop.index = high_stay_prop.index.astype(str)
        high_stay_prop.columns = high_stay_prop.columns.astype(str)
        # Reindex to ensure all temp_cat and combined categories are present
        all_temp_cats = ['Low', 'Med', 'High']
        all_hum_precip_combos = sorted(df_yearly['hum_precip_combined'].unique())
        high_stay_prop = high_stay_prop.reindex(index=all_temp_cats, columns=all_hum_precip_combos, fill_value=0)
        
        # Create the heatmap with explicit row labels for temp_cat
        plt.figure(figsize=(12, 8))  # Larger for combined labels
        sns.heatmap(high_stay_prop, annot=True, fmt='.2f', cmap='YlOrRd', cbar_kws={'label': 'Proportion of High Stay'})
        # Explicitly set y-axis labels to temp_cat only (Low, Med, High)
        plt.yticks(ticks=np.arange(len(all_temp_cats)) + 0.5, labels=all_temp_cats, rotation=0)
        plt.title(f'{elephant_id} - {year}: Proportion of High Stay by Temperature Categories (Hum-Precip Combined)')
        plt.xlabel('Humidity-Precipitation Category (e.g., Low-Low)')
        plt.ylabel('Temperature Category')
        plt.xticks(rotation=45, ha='right')
        plot_path7_yearly = os.path.join(elephant_year_plots, f'{elephant_id}_high_stay_prop_heatmap_{year}_yearly.png')
        plt.savefig(plot_path7_yearly, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved yearly heatmap: {plot_path7_yearly}")
    else:
        print("Skipping yearly heatmap: No data")
    
    # New Plot 7: Month-wise Heatmap of High Stay Proportion by Temp and Hum/Precip Categories (fixed labeling and reindex)
    if available_months:
        for month in available_months:
            month_name = month_abbr[month][:3]
            df_month = df[df['month'] == month].copy()
            if len(df_month) == 0:
                print(f"Skipping heatmap for {month_name}: No data")
                continue
            # Recompute categories for this month (using month's quantiles for bins)
            df_month['temp_cat'] = pd.cut(df_month['temp_c'], bins=3, labels=['Low', 'Med', 'High'])
            df_month['hum_cat'] = pd.cut(df_month['humidity_percent'], bins=3, labels=['Low', 'Med', 'High'])
            df_month['precip_cat'] = pd.cut(df_month['Precip_mm'], bins=3, labels=['Low', 'Med', 'High'])
            month_stay_high_thresh = df_month['stay_duration_hours'].median()
            df_month['stay_cat'] = np.where(df_month['stay_duration_hours'] > month_stay_high_thresh, 'High', 'Low')
            df_month['hum_precip_combined'] = df_month['hum_cat'].astype(str) + '-' + df_month['precip_cat'].astype(str)
            
            crosstab_stay = pd.crosstab([df_month['temp_cat'], df_month['hum_precip_combined']], df_month['stay_cat'], normalize='index')  # Proportions
            # Safely get 'High' column, default to zeros if missing
            high_stay_series = crosstab_stay.get('High', pd.Series(0, index=crosstab_stay.index))
            high_stay_prop = high_stay_series.unstack(fill_value=0)
            # Convert index to regular strings to avoid CategoricalIndex issues
            high_stay_prop.index = high_stay_prop.index.astype(str)
            high_stay_prop.columns = high_stay_prop.columns.astype(str)
            # Reindex to ensure all temp_cat and combined categories are present (no 'level' arg)
            all_temp_cats = ['Low', 'Med', 'High']
            all_hum_precip_combos = sorted(df_month['hum_precip_combined'].unique())
            high_stay_prop = high_stay_prop.reindex(index=all_temp_cats, columns=all_hum_precip_combos, fill_value=0)
            # Create the heatmap with explicit row labels for temp_cat
            plt.figure(figsize=(12, 8))  # Larger for combined labels
            sns.heatmap(high_stay_prop, annot=True, fmt='.2f', cmap='YlOrRd', cbar_kws={'label': 'Proportion of High Stay'})
            # Explicitly set y-axis labels to temp_cat only (Low, Med, High)
            plt.yticks(ticks=np.arange(len(all_temp_cats)) + 0.5, labels=all_temp_cats, rotation=0)
            plt.title(f'{elephant_id} - {year} - {month_name}: Proportion of High Stay by Temperature Categories (Hum-Precip Combined)')
            plt.xlabel('Humidity-Precipitation Category (e.g., Low-Low)')
            plt.ylabel('Temperature Category')
            plt.xticks(rotation=45, ha='right')
            plot_path7 = os.path.join(elephant_year_plots, f'{elephant_id}_high_stay_prop_heatmap_{year}_month_{month}.png')
            plt.savefig(plot_path7, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved month-wise heatmap for {month_name}: {plot_path7}")

print(f"\nAll per-elephant-year analyses completed. Enhanced CSVs and plots in: {analysis_dir}")
print("Enhanced CSVs include 'stay_cat' (High/Low based on median stay duration) and other categories.")

# Final debug: List contents of analysis_dir
print(f"\nContents of {analysis_dir}:")
if os.path.exists(analysis_dir):
    contents = os.listdir(analysis_dir)
    for item in contents:
        item_path = os.path.join(analysis_dir, item)
        if os.path.isdir(item_path):
            print(f" [DIR] {item}")
        else:
            print(f" [FILE] {item}")
else:
    print("Analysis directory does not exist!")