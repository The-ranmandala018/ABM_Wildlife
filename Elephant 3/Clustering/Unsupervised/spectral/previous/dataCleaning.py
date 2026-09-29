'''Without dialing aggregating'''

# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import StandardScaler
# import matplotlib.pyplot as plt
# import seaborn as sns
# from pathlib import Path

# # Set up output directory
# RESULT = Path("cleanedData")
# RESULT.mkdir(parents=True, exist_ok=True)

# # Load data
# df_tracking = pd.read_csv('from_2010.csv')

# # Convert datetime
# df_tracking['datetime_parsed'] = pd.to_datetime(df_tracking['datetime'], format='%m/%d/%Y %H:%M', errors='coerce')

# # Drop redundant columns early
# df_tracking = df_tracking.drop(columns=['Date', 'timeAPM', 'Time', 'datetime', 'geometry'], errors='ignore')

# # Missing values check
# print("Missing Values:\n", df_tracking.isnull().sum())

# # === Outlier Clipping ===
# num_cols = ['step_length', 'dt_sec', 'speed', 'residence_time', 'bearing', 'turning_angle']
# for col in num_cols:
#     Q1 = df_tracking[col].quantile(0.25)
#     Q3 = df_tracking[col].quantile(0.75)
#     IQR = Q3 - Q1
#     lower = Q1 - 1.5 * IQR
#     upper = Q3 + 1.5 * IQR
#     clipped_count = ((df_tracking[col] < lower) | (df_tracking[col] > upper)).sum()
#     df_tracking[col] = np.clip(df_tracking[col], lower, upper)
#     print(f"Clipped {clipped_count} outliers in {col} (bounds: {lower:.2f} to {upper:.2f})")

# # Save cleaned (clipped) data
# df_tracking.to_csv(RESULT / 'tracking_cleaned_clipped.csv', index=False)
# print("\nCleaned (clipped) data saved.")

# # === Standardization (Scaling) ===
# # Features to scale (same as used for clustering)
# features_to_scale = ['Longitude', 'Latitude', 'step_length', 'speed', 'bearing', 'turning_angle', 'residence_time']

# scaler = StandardScaler()
# scaled_data = scaler.fit_transform(df_tracking[features_to_scale])

# # Create a new DataFrame with scaled features
# df_scaled = pd.DataFrame(scaled_data, columns=[f"{col}_scaled" for col in features_to_scale])

# # Add back non-scaled columns (like datetime) if needed for reference
# df_scaled['datetime_parsed'] = df_tracking['datetime_parsed'].values

# # Reorder columns for clarity
# cols_order = ['datetime_parsed'] + [f"{col}_scaled" for col in features_to_scale]
# df_scaled = df_scaled[cols_order]

# # Save scaled data (ideal for clustering)
# df_scaled.to_csv(RESULT / 'tracking_scaled_for_clustering.csv', index=False)
# print("Scaled data saved for clustering.")

# # === Summary after scaling ===
# print("\nScaled Features Description:")
# print(df_scaled[[f"{col}_scaled" for col in features_to_scale]].describe())

# # === Correlation Heatmap (on original clipped data - more interpretable) ===
# corr_cols = num_cols + ['Longitude', 'Latitude']
# plt.figure(figsize=(12, 10))
# sns.heatmap(df_tracking[corr_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f')
# plt.title('Correlation Heatmap (After Clipping)')
# plt.savefig(RESULT / 'correlation_heatmap_clipped.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Correlation heatmap (clipped data) saved.")

# # === Distribution Plots: Before Scaling ===
# print("\nGenerating distribution plots BEFORE scaling...")
# for col in ['speed', 'step_length', 'turning_angle']:
#     plt.figure(figsize=(8, 6))
#     sns.histplot(df_tracking[col], kde=True, color='skyblue')
#     plt.title(f'Distribution of {col} (Before Scaling)')
#     plt.xlabel(col)
#     plt.ylabel('Frequency')
#     filename = f"distribution_before_{col}.png"
#     plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Saved: {filename}")

# # === Distribution Plots: After Scaling ===
# print("\nGenerating distribution plots AFTER scaling...")
# scaled_cols = ['speed_scaled', 'step_length_scaled', 'turning_angle_scaled']
# for col in scaled_cols:
#     original_name = col.replace('_scaled', '')
#     plt.figure(figsize=(8, 6))
#     sns.histplot(df_scaled[col], kde=True, color='orange')
#     plt.title(f'Distribution of {original_name} (After Standardization)')
#     plt.xlabel(f'{original_name} (z-score)')
#     plt.ylabel('Frequency')
#     filename = f"distribution_after_{original_name}.png"
#     plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Saved: {filename}")

# # Optional: Pairplot of scaled features (useful for clustering insight)
# print("\nGenerating pairplot of scaled features...")
# sns.pairplot(df_scaled[scaled_cols], diag_kind='kde')
# plt.suptitle('Pairplot of Scaled Features', y=1.02)
# plt.savefig(RESULT / 'pairplot_scaled_features.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Pairplot of scaled features saved.")

# print("\nAll tasks completed!")
# print("Check the 'cleanedData' folder for:")
# print("   - tracking_cleaned_clipped.csv")
# print("   - tracking_scaled_for_clustering.csv")
# print("   - All plots (before/after scaling, correlation, pairplot)")






# '''Including clipping'''

# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import StandardScaler
# from scipy.spatial import ConvexHull
# import matplotlib.pyplot as plt
# import seaborn as sns
# from pathlib import Path

# # Set up output directory
# RESULT = Path("DailyData")
# RESULT.mkdir(parents=True, exist_ok=True)

# # Load original tracking data
# df_tracking = pd.read_csv('from_2010.csv')

# # Convert datetime
# df_tracking['datetime_parsed'] = pd.to_datetime(df_tracking['datetime'], format='%m/%d/%Y %H:%M', errors='coerce')

# # Extract date for aggregation
# df_tracking['date'] = df_tracking['datetime_parsed'].dt.date

# # Drop redundant columns
# df_tracking = df_tracking.drop(columns=['Date', 'timeAPM', 'Time', 'datetime', 'geometry'], errors='ignore')

# print("Original data shape:", df_tracking.shape)
# print("Date range:", df_tracking['date'].min(), "to", df_tracking['date'].max())

# # ===============================
# # 1. DAILY AGGREGATION (YOUR EXACT VERSION)
# # ===============================
# print("\nAggregating data to daily level...")

# def calculate_convex_hull_area(group):
#     points = group[['Longitude', 'Latitude']].values
#     if len(points) < 3:
#         return 0.0
#     try:
#         hull = ConvexHull(points)
#         return hull.area  # Area in (decimal degrees)^2
#     except:
#         return 0.0

# daily_agg = df_tracking.groupby('date').apply(lambda g: pd.Series({
#     'num_gps_fixes': len(g),
#     'centroid_lon': g['Longitude'].mean(),
#     'centroid_lat': g['Latitude'].mean(),
#     'mean_stepLength': g['step_length'].mean(),
#     'totdistance': g['step_length'].sum(),
#     'mean_speed': g['speed'].mean(),
#     'speed_variance': g['speed'].std(),
#     'mean_turning_angle': g['turning_angle'].mean(),
#     'std_turning_angle': g['turning_angle'].std(),  # tortuosity proxy
#     'daily_total_residence_time': g['residence_time'].sum(),
#     'daily_mean_bearing': g['bearing'].mean(),
#     'daily_area_sq_deg': calculate_convex_hull_area(g)
# })).reset_index()

# # Fill NaN in std columns (days with only 1 fix)
# daily_agg['speed_variance'].fillna(0, inplace=True)
# daily_agg['std_turning_angle'].fillna(0, inplace=True)

# print("Daily aggregated data shape:", daily_agg.shape)

# # Save raw aggregated data (before any clipping)
# daily_agg.to_csv(RESULT / 'tracking_daily_raw_aggregated.csv', index=False)
# print("Raw daily aggregated data saved.")

# # ===============================
# # 2. EDA & PLOTS: BEFORE CLIPPING (on raw aggregated)
# # ===============================
# print("\nGenerating plots BEFORE clipping...")

# plot_cols_raw = ['totdistance', 'mean_speed', 'std_turning_angle', 
#                  'daily_total_residence_time', 'daily_area_sq_deg', 'mean_stepLength']

# # Correlation heatmap (before clipping)
# plt.figure(figsize=(14, 10))
# sns.heatmap(daily_agg[plot_cols_raw].corr(), annot=True, cmap='coolwarm', fmt='.2f')
# plt.title('Correlation Heatmap - Raw Daily Aggregated Features')
# plt.savefig(RESULT / 'correlation_before_clipping.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Correlation heatmap (before clipping) saved.")

# # Distribution plots BEFORE clipping
# for col in plot_cols_raw:
#     plt.figure(figsize=(8, 6))
#     sns.histplot(daily_agg[col], kde=True, color='lightgreen')
#     plt.title(f'Distribution of {col} (Raw Aggregated - Before Clipping)')
#     plt.xlabel(col)
#     plt.ylabel('Frequency')
#     filename = f"distribution_raw_{col}.png"
#     plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Saved: {filename}")

# # ===============================
# # 3. OUTLIER CLIPPING
# # ===============================
# print("\nClipping outliers...")

# clip_cols = ['mean_stepLength', 'totdistance', 'mean_speed', 'speed_variance',
#              'std_turning_angle', 'daily_total_residence_time', 'daily_area_sq_deg']

# for col in clip_cols:
#     Q1 = daily_agg[col].quantile(0.25)
#     Q3 = daily_agg[col].quantile(0.75)
#     IQR = Q3 - Q1
#     lower = Q1 - 1.5 * IQR
#     upper = Q3 + 1.5 * IQR
#     clipped_count = ((daily_agg[col] < lower) | (daily_agg[col] > upper)).sum()
#     daily_agg[col] = np.clip(daily_agg[col], lower, upper)
#     print(f"Clipped {clipped_count} outliers in {col}")

# # Save clipped data
# daily_agg.to_csv(RESULT / 'tracking_daily_clipped.csv', index=False)
# print("Clipped daily data saved.")

# # ===============================
# # 4. PLOTS: AFTER CLIPPING (before scaling)
# # ===============================
# print("\nGenerating plots AFTER clipping (before scaling)...")

# # Correlation after clipping
# plt.figure(figsize=(14, 10))
# sns.heatmap(daily_agg[plot_cols_raw].corr(), annot=True, cmap='coolwarm', fmt='.2f')
# plt.title('Correlation Heatmap - After Clipping')
# plt.savefig(RESULT / 'correlation_after_clipping.png', dpi=300, bbox_inches='tight')
# plt.close()

# # Distributions after clipping
# for col in plot_cols_raw:
#     plt.figure(figsize=(8, 6))
#     sns.histplot(daily_agg[col], kde=True, color='skyblue')
#     plt.title(f'Distribution of {col} (After Clipping)')
#     plt.xlabel(col)
#     plt.ylabel('Frequency')
#     filename = f"distribution_clipped_{col}.png"
#     plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Saved: {filename}")

# # ===============================
# # 5. SCALING (Standardization)
# # ===============================
# features_to_scale = ['mean_stepLength', 'totdistance', 'mean_speed', 'speed_variance',
#                      'std_turning_angle', 'daily_total_residence_time', 'daily_area_sq_deg',
#                      'centroid_lon', 'centroid_lat']

# scaler = StandardScaler()
# scaled_data = scaler.fit_transform(daily_agg[features_to_scale])

# df_daily_scaled = pd.DataFrame(scaled_data, columns=[f"{col}_scaled" for col in features_to_scale])
# df_daily_scaled['date'] = daily_agg['date']
# df_daily_scaled['num_gps_fixes'] = daily_agg['num_gps_fixes']

# # Reorder
# cols_order = ['date', 'num_gps_fixes'] + [f"{col}_scaled" for col in features_to_scale]
# df_daily_scaled = df_daily_scaled[cols_order]

# # Save scaled data
# df_daily_scaled.to_csv(RESULT / 'tracking_daily_scaled_for_clustering.csv', index=False)
# print("\nScaled daily data saved.")

# # ===============================
# # 6. PLOTS: AFTER SCALING
# # ===============================
# print("\nGenerating plots AFTER scaling...")

# scaled_plot_cols = ['totdistance_scaled', 'mean_speed_scaled', 'std_turning_angle_scaled',
#                     'daily_total_residence_time_scaled', 'daily_area_sq_deg_scaled']

# # Pairplot after scaling
# sns.pairplot(df_daily_scaled[scaled_plot_cols], diag_kind='kde')
# plt.suptitle('Pairplot of Key Scaled Daily Features', y=1.02)
# plt.savefig(RESULT / 'pairplot_after_scaling.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Pairplot after scaling saved.")

# # Individual distributions after scaling
# for col in scaled_plot_cols:
#     orig_name = col.replace('_scaled', '')
#     plt.figure(figsize=(8, 6))
#     sns.histplot(df_daily_scaled[col], kde=True, color='orange')
#     plt.title(f'Distribution of {orig_name} (After Scaling)')
#     plt.xlabel(f'{orig_name} (z-score)')
#     plt.ylabel('Frequency')
#     filename = f"distribution_scaled_{orig_name}.png"
#     plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Saved: {filename}")

# # Bonus: Time series of total distance and area
# fig, ax1 = plt.subplots(figsize=(14, 6))
# ax1.plot(daily_agg['date'], daily_agg['totdistance'], color='darkgreen')
# ax1.set_xlabel('Date')
# ax1.set_ylabel('Total Daily Distance (m)', color='darkgreen')
# ax1.tick_params(axis='y', labelcolor='darkgreen')

# ax2 = ax1.twinx()
# ax2.plot(daily_agg['date'], daily_agg['daily_area_sq_deg'], color='purple')
# ax2.set_ylabel('Daily Area (sq decimal degrees)', color='purple')
# ax2.tick_params(axis='y', labelcolor='purple')

# plt.title('Daily Total Distance and Area Covered (After Clipping)')
# plt.grid(True, alpha=0.3)
# plt.savefig(RESULT / 'timeseries_distance_area.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Time series plot saved.")

# print("\n=== ALL DONE ===")
# print("Files saved in 'DailyData' folder:")
# print("   - tracking_daily_raw_aggregated.csv")
# print("   - tracking_daily_clipped.csv")
# print("   - tracking_daily_scaled_for_clustering.csv")
# print("   - All plots: before clipping, after clipping, after scaling")


'''No clipping & saving Outliers'''

# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import StandardScaler
# from scipy.spatial import ConvexHull
# import matplotlib.pyplot as plt
# import seaborn as sns
# from pathlib import Path

# # Set up output directory
# RESULT = Path("DailyData")
# RESULT.mkdir(parents=True, exist_ok=True)

# # Load original tracking data
# df_tracking = pd.read_csv('from_2010.csv')

# # Convert datetime
# df_tracking['datetime_parsed'] = pd.to_datetime(df_tracking['datetime'], format='%m/%d/%Y %H:%M', errors='coerce')

# # Extract date for aggregation
# df_tracking['date'] = df_tracking['datetime_parsed'].dt.date

# # Drop redundant columns
# df_tracking = df_tracking.drop(columns=['Date', 'timeAPM', 'Time', 'datetime', 'geometry'], errors='ignore')

# print("Original data shape:", df_tracking.shape)
# print("Date range:", df_tracking['date'].min(), "to", df_tracking['date'].max())

# # ===============================
# # 1. DAILY AGGREGATION (Your Exact Specification)
# # ===============================
# print("\nAggregating data to daily level...")

# def calculate_convex_hull_area(group):
#     points = group[['Longitude', 'Latitude']].values
#     if len(points) < 3:
#         return 0.0
#     try:
#         hull = ConvexHull(points)
#         return hull.area  # Area in (decimal degrees)^2
#     except:
#         return 0.0

# daily_agg = df_tracking.groupby('date').apply(lambda g: pd.Series({
#     'num_gps_fixes': len(g),
#     'centroid_lon': g['Longitude'].mean(),
#     'centroid_lat': g['Latitude'].mean(),
#     'mean_stepLength': g['step_length'].mean(),
#     'totdistance': g['step_length'].sum(),
#     'mean_speed': g['speed'].mean(),
#     'speed_variance': g['speed'].std(),
#     'mean_turning_angle': g['turning_angle'].mean(),
#     'std_turning_angle': g['turning_angle'].std(),  # Tortuosity proxy
#     'daily_total_residence_time': g['residence_time'].sum(),
#     'daily_mean_bearing': g['bearing'].mean(),
#     'daily_area_sq_deg': calculate_convex_hull_area(g)
# })).reset_index()

# # Fill NaN in std columns (days with only 1 fix)
# daily_agg['speed_variance'].fillna(0, inplace=True)
# daily_agg['std_turning_angle'].fillna(0, inplace=True)

# print("Daily aggregated data shape:", daily_agg.shape)
# print(daily_agg.head())

# # Save raw daily aggregated data
# daily_agg.to_csv(RESULT / 'tracking_daily_aggregated.csv', index=False)
# print("Raw daily aggregated data saved.")

# # ===============================
# # 2. DETECT OUTLIERS (NO CLIPPING) → Save separately
# # ===============================
# print("\nDetecting outliers (IQR method) and saving to separate file...")

# outlier_columns = [
#     'mean_stepLength', 'totdistance', 'mean_speed', 'speed_variance',
#     'std_turning_angle', 'daily_total_residence_time', 'daily_area_sq_deg'
# ]

# outlier_flags = pd.DataFrame()
# daily_agg_with_flags = daily_agg.copy()

# for col in outlier_columns:
#     Q1 = daily_agg[col].quantile(0.25)
#     Q3 = daily_agg[col].quantile(0.75)
#     IQR = Q3 - Q1
#     lower = Q1 - 1.5 * IQR
#     upper = Q3 + 1.5 * IQR
#     is_outlier = (daily_agg[col] < lower) | (daily_agg[col] > upper)
#     daily_agg_with_flags[f'{col}_is_outlier'] = is_outlier
#     print(f"{col}: {is_outlier.sum()} outliers detected (bounds: {lower:.4f} to {upper:.4f})")

# # Extract rows with at least one outlier
# outliers_df = daily_agg_with_flags[daily_agg_with_flags[[f'{col}_is_outlier' for col in outlier_columns]].any(axis=1)].copy()
# outliers_df = outliers_df.drop(columns=[f'{col}_is_outlier' for col in outlier_columns])  # Clean up flags

# # Save outliers separately
# outliers_df.to_csv(RESULT / 'tracking_daily_outliers.csv', index=False)
# print(f"Outlier rows saved: {len(outliers_df)} rows → tracking_daily_outliers.csv")

# # Proceed with RAW daily_agg (no clipping)
# print("Proceeding with raw (unclipped) daily data for scaling.")

# # ===============================
# # 3. SCALING (Standardization) on Raw Daily Data
# # ===============================
# features_to_scale = [
#     'mean_stepLength', 'totdistance', 'mean_speed', 'speed_variance',
#     'std_turning_angle', 'daily_total_residence_time', 'daily_area_sq_deg',
#     'centroid_lon', 'centroid_lat'
# ]

# scaler = StandardScaler()
# scaled_data = scaler.fit_transform(daily_agg[features_to_scale])

# df_daily_scaled = pd.DataFrame(scaled_data, columns=[f"{col}_scaled" for col in features_to_scale])
# df_daily_scaled['date'] = daily_agg['date']
# df_daily_scaled['num_gps_fixes'] = daily_agg['num_gps_fixes']

# # Reorder
# cols_order = ['date', 'num_gps_fixes'] + [f"{col}_scaled" for col in features_to_scale]
# df_daily_scaled = df_daily_scaled[cols_order]

# # Save scaled data
# df_daily_scaled.to_csv(RESULT / 'tracking_daily_scaled_for_clustering.csv', index=False)
# print("\nScaled daily data (from raw aggregation) saved.")

# # Summary after scaling
# print("\nScaled Features Description:")
# print(df_daily_scaled[[f"{col}_scaled" for col in features_to_scale]].describe())

# # ===============================
# # 4. PLOTS
# # ===============================

# # Correlation heatmap (raw daily data)
# plt.figure(figsize=(14, 10))
# corr_features = features_to_scale
# sns.heatmap(daily_agg[corr_features].corr(), annot=True, cmap='coolwarm', fmt='.2f')
# plt.title('Correlation Heatmap - Daily Features (Raw Aggregated)')
# plt.savefig(RESULT / 'correlation_heatmap_daily_raw.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Correlation heatmap (raw) saved.")

# # Distribution plots BEFORE scaling (right after aggregation)
# print("\nGenerating distribution plots BEFORE scaling...")
# plot_cols_before = ['totdistance', 'mean_speed', 'std_turning_angle',
#                     'daily_total_residence_time', 'daily_area_sq_deg', 'mean_stepLength']

# for col in plot_cols_before:
#     plt.figure(figsize=(8, 6))
#     sns.histplot(daily_agg[col], kde=True, color='skyblue')
#     nice_name = col.replace('_', ' ').title()
#     plt.title(f'Distribution of {nice_name} (Before Scaling)')
#     plt.xlabel(nice_name)
#     plt.ylabel('Frequency')
#     filename = f"distribution_before_{col}.png"
#     plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Saved: {filename}")

# # Distribution plots AFTER scaling
# print("\nGenerating distribution plots AFTER scaling...")
# plot_cols_after = ['totdistance_scaled', 'mean_speed_scaled', 'std_turning_angle_scaled',
#                    'daily_total_residence_time_scaled', 'daily_area_sq_deg_scaled', 'mean_stepLength_scaled']

# for col in plot_cols_after:
#     orig_name = col.replace('_scaled', '').replace('_', ' ').title()
#     plt.figure(figsize=(8, 6))
#     sns.histplot(df_daily_scaled[col], kde=True, color='orange')
#     plt.title(f'Distribution of {orig_name} (After Standardization)')
#     plt.xlabel(f'{orig_name} (z-score)')
#     plt.ylabel('Frequency')
#     filename = f"distribution_after_{col.replace('_scaled', '')}.png"
#     plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"Saved: {filename}")

# # Pairplot of key scaled features
# print("\nGenerating pairplot...")
# sns.pairplot(df_daily_scaled[plot_cols_after], diag_kind='kde')
# plt.suptitle('Pairplot of Key Scaled Daily Features', y=1.02)
# plt.savefig(RESULT / 'pairplot_daily_scaled_features.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Pairplot saved.")

# # Time series: Total distance and area
# fig, ax1 = plt.subplots(figsize=(14, 6))
# ax1.plot(daily_agg['date'], daily_agg['totdistance'], color='darkgreen')
# ax1.set_xlabel('Date')
# ax1.set_ylabel('Total Distance (m)', color='darkgreen')
# ax1.tick_params(axis='y', labelcolor='darkgreen')
# ax1.set_title('Daily Total Distance and Area Covered (2010–2013)')

# ax2 = ax1.twinx()
# ax2.plot(daily_agg['date'], daily_agg['daily_area_sq_deg'], color='purple')
# ax2.set_ylabel('Daily Area (sq deg)', color='purple')
# ax2.tick_params(axis='y', labelcolor='purple')

# fig.tight_layout()
# plt.savefig(RESULT / 'timeseries_distance_and_area.png', dpi=300, bbox_inches='tight')
# plt.close()
# print("Time series plot saved.")

# print("\n=== ALL DONE ===")
# print("Outputs in 'DailyData' folder:")
# print("   - tracking_daily_aggregated.csv")
# print("   - tracking_daily_outliers.csv")
# print("   - tracking_daily_scaled_for_clustering.csv")
# print("   - All plots (before/after scaling, correlation, pairplot, time series)")




'''Temperature'''

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up output directory
RESULT = Path("cleanedData")
RESULT.mkdir(parents=True, exist_ok=True)

# Load data
df_tracking = pd.read_csv('from_2010.csv')

# Convert datetime
df_tracking['datetime_parsed'] = pd.to_datetime(df_tracking['datetime'], format='%m/%d/%Y %H:%M', errors='coerce')

# Drop redundant columns early
df_tracking = df_tracking.drop(columns=['Date', 'timeAPM', 'Time', 'datetime', 'geometry'], errors='ignore')

# Missing values check
print("Missing Values:\n", df_tracking.isnull().sum())

# === Outlier Clipping ===
num_cols = ['step_length', 'dt_sec', 'speed', 'residence_time', 'bearing', 'turning_angle']
for col in num_cols:
    Q1 = df_tracking[col].quantile(0.25)
    Q3 = df_tracking[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    clipped_count = ((df_tracking[col] < lower) | (df_tracking[col] > upper)).sum()
    df_tracking[col] = np.clip(df_tracking[col], lower, upper)
    print(f"Clipped {clipped_count} outliers in {col} (bounds: {lower:.2f} to {upper:.2f})")

# Save cleaned (clipped) data
df_tracking.to_csv(RESULT / 'tracking_cleaned_clipped.csv', index=False)
print("\nCleaned (clipped) data saved.")

# === Standardization (Scaling) ===
# Features to scale (same as used for clustering)
features_to_scale = ['Longitude', 'Latitude', 'step_length', 'speed', 'bearing', 'turning_angle', 'residence_time']

scaler = StandardScaler()
scaled_data = scaler.fit_transform(df_tracking[features_to_scale])

# Create a new DataFrame with scaled features
df_scaled = pd.DataFrame(scaled_data, columns=[f"{col}_scaled" for col in features_to_scale])

# Add back non-scaled columns (like datetime) if needed for reference
df_scaled['datetime_parsed'] = df_tracking['datetime_parsed'].values

# Reorder columns for clarity
cols_order = ['datetime_parsed'] + [f"{col}_scaled" for col in features_to_scale]
df_scaled = df_scaled[cols_order]

# Save scaled data (ideal for clustering)
df_scaled.to_csv(RESULT / 'tracking_scaled_for_clustering.csv', index=False)
print("Scaled data saved for clustering.")

# === Summary after scaling ===
print("\nScaled Features Description:")
print(df_scaled[[f"{col}_scaled" for col in features_to_scale]].describe())

# === Correlation Heatmap (on original clipped data - more interpretable) ===
corr_cols = num_cols + ['Longitude', 'Latitude']
plt.figure(figsize=(12, 10))
sns.heatmap(df_tracking[corr_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Heatmap (After Clipping)')
plt.savefig(RESULT / 'correlation_heatmap_clipped.png', dpi=300, bbox_inches='tight')
plt.close()
print("Correlation heatmap (clipped data) saved.")

# === Distribution Plots: Before Scaling ===
print("\nGenerating distribution plots BEFORE scaling...")
for col in ['speed', 'step_length', 'turning_angle']:
    plt.figure(figsize=(8, 6))
    sns.histplot(df_tracking[col], kde=True, color='skyblue')
    plt.title(f'Distribution of {col} (Before Scaling)')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    filename = f"distribution_before_{col}.png"
    plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")

# === Distribution Plots: After Scaling ===
print("\nGenerating distribution plots AFTER scaling...")
scaled_cols = ['speed_scaled', 'step_length_scaled', 'turning_angle_scaled']
for col in scaled_cols:
    original_name = col.replace('_scaled', '')
    plt.figure(figsize=(8, 6))
    sns.histplot(df_scaled[col], kde=True, color='orange')
    plt.title(f'Distribution of {original_name} (After Standardization)')
    plt.xlabel(f'{original_name} (z-score)')
    plt.ylabel('Frequency')
    filename = f"distribution_after_{original_name}.png"
    plt.savefig(RESULT / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")

# Optional: Pairplot of scaled features (useful for clustering insight)
print("\nGenerating pairplot of scaled features...")
sns.pairplot(df_scaled[scaled_cols], diag_kind='kde')
plt.suptitle('Pairplot of Scaled Features', y=1.02)
plt.savefig(RESULT / 'pairplot_scaled_features.png', dpi=300, bbox_inches='tight')
plt.close()
print("Pairplot of scaled features saved.")

print("\nAll tasks completed!")
print("Check the 'cleanedData' folder for:")
print("   - tracking_cleaned_clipped.csv")
print("   - tracking_scaled_for_clustering.csv")
print("   - All plots (before/after scaling, correlation, pairplot)")