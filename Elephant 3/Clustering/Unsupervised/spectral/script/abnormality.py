import os
import pandas as pd
import numpy as np
from collections import defaultdict

# ==========================================================
# PATH SETUP
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "segments")
ANOMALIES_DIR = os.path.join(BASE_DIR, "..", "anomalies")
os.makedirs(ANOMALIES_DIR, exist_ok=True)

# ==========================================================
# ANOMALY DETECTION FUNCTION
# ==========================================================
def detect_anomalies(csv_path, output_dir):
    file_id = os.path.basename(csv_path).split("_")[0]
    anomaly_report_path = os.path.join(output_dir, f"{file_id}_anomalies_report.txt")
    anomaly_csv_path = os.path.join(output_dir, f"{file_id}_abnormal_data.csv")
    
    anomaly_indices = set()
    anomaly_types = defaultdict(list)
    
    with open(anomaly_report_path, 'w') as report_file:
        report_file.write(f"Anomaly Report for: {csv_path}\n")
        report_file.write("=" * 80 + "\n\n")
        
        try:
            df = pd.read_csv(csv_path)
            report_file.write("1. Data Loading: Successful\n")
        except Exception as e:
            report_file.write(f"1. Data Loading: Failed - {str(e)}\n")
            return
        
        # Convert datetime
        try:
            df["datetime"] = pd.to_datetime(df["datetime"])
            report_file.write("2. Datetime Parsing: Successful\n")
        except Exception as e:
            report_file.write(f"2. Datetime Parsing: Failed - {str(e)}\n")
        
        # Check for missing values
        missing_rows = df[df.isnull().any(axis=1)].index
        for idx in missing_rows:
            anomaly_indices.add(idx)
            anomaly_types[idx].append("missing_values")
        missing = df.isnull().sum()
        report_file.write("3. Missing Values:\n")
        for col, count in missing.items():
            report_file.write(f"   - {col}: {count} missing\n")
        report_file.write(f"   - Rows with missing values: {len(missing_rows)}\n\n")
        
        # Check for duplicate rows
        duplicate_rows = df[df.duplicated(keep=False)].index
        for idx in duplicate_rows:
            anomaly_indices.add(idx)
            anomaly_types[idx].append("duplicate_row")
        duplicates = df.duplicated().sum()
        report_file.write(f"4. Duplicate Rows: {duplicates} (marked all occurrences: {len(duplicate_rows)})\n\n")
        
        # Check non-increasing datetime
        if "datetime" in df.columns:
            non_increasing_mask = df["datetime"].diff().dt.total_seconds() <= 0
            non_increasing_rows = df[non_increasing_mask].index
            for idx in non_increasing_rows:
                anomaly_indices.add(idx)
                anomaly_types[idx].append("non_increasing_datetime")
            non_increasing = non_increasing_mask.sum()
            report_file.write(f"5. Non-increasing Datetime: {non_increasing} instances\n\n")
        
        # Check geographic coordinates
        if "Longitude" in df.columns and "Latitude" in df.columns:
            invalid_lon_mask = (df["Longitude"] < -180) | (df["Longitude"] > 180)
            invalid_lon_rows = df[invalid_lon_mask].index
            for idx in invalid_lon_rows:
                anomaly_indices.add(idx)
                anomaly_types[idx].append("invalid_longitude")
            invalid_lon = invalid_lon_mask.sum()
            
            invalid_lat_mask = (df["Latitude"] < -90) | (df["Latitude"] > 90)
            invalid_lat_rows = df[invalid_lat_mask].index
            for idx in invalid_lat_rows:
                anomaly_indices.add(idx)
                anomaly_types[idx].append("invalid_latitude")
            invalid_lat = invalid_lat_mask.sum()
            
            report_file.write(f"6. Invalid Longitude: {invalid_lon} (outside -180 to 180)\n")
            report_file.write(f"7. Invalid Latitude: {invalid_lat} (outside -90 to 90)\n\n")
        
        # Check step_length
        if "step_length" in df.columns:
            negative_step_mask = df["step_length"] < 0
            negative_step_rows = df[negative_step_mask].index
            for idx in negative_step_rows:
                anomaly_indices.add(idx)
                anomaly_types[idx].append("negative_step_length")
            negative_step = negative_step_mask.sum()
            report_file.write(f"8. Negative Step Length: {negative_step}\n\n")
        
        # Check turning_angle (assuming degrees, -180 to 180)
        if "turning_angle" in df.columns:
            invalid_turn_mask = (df["turning_angle"] < -180) | (df["turning_angle"] > 180)
            invalid_turn_rows = df[invalid_turn_mask].index
            for idx in invalid_turn_rows:
                anomaly_indices.add(idx)
                anomaly_types[idx].append("invalid_turning_angle")
            invalid_turn = invalid_turn_mask.sum()
            report_file.write(f"9. Invalid Turning Angle: {invalid_turn} (outside -180 to 180)\n\n")
        
        # Additional stats
        report_file.write("10. Summary Statistics:\n")
        try:
            stats = df.describe(include='all')
            report_file.write(stats.to_string() + "\n")
        except:
            report_file.write("Unable to generate summary statistics.\n")
        
        # Save abnormal data to CSV
        if anomaly_indices:
            abnormal_df = df.loc[sorted(anomaly_indices)].copy()
            abnormal_df['anomaly_types'] = [', '.join(anomaly_types[idx]) for idx in abnormal_df.index]
            abnormal_df.to_csv(anomaly_csv_path, index=True, index_label='original_index')
            report_file.write(f"\n11. Abnormal data saved to: {anomaly_csv_path}\n")
            report_file.write(f"   - Total abnormal rows: {len(abnormal_df)}\n")
        else:
            report_file.write("\n11. No abnormal data found.\n")
    
    print(f"Anomaly report saved for {csv_path} at {anomaly_report_path}")
    if anomaly_indices:
        print(f"Abnormal data CSV saved at {anomaly_csv_path}")

# ==========================================================
# BATCH PROCESS
# ==========================================================
for group in ["fe", "me"]:
    group_dir = os.path.join(SEGMENTS_DIR, group)
    anomaly_group_dir = os.path.join(ANOMALIES_DIR, group)
    os.makedirs(anomaly_group_dir, exist_ok=True)
    
    for file in sorted(os.listdir(group_dir)):
        if not file.endswith(".csv"):
            continue
        csv_path = os.path.join(group_dir, file)
        print(f"\nProcessing: {csv_path}")
        detect_anomalies(csv_path, anomaly_group_dir)