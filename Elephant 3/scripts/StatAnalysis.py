###### standard devialtion of total distance vs date

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ------------------- CONFIG -------------------
BASE_PATH = "../scripts/clustering_data"
OUTPUT_ROOT = "../Statistical_results_std"
ROLLING_WINDOW = 30  # days for rolling std

# Load all data
def load_all_clustered_features():
    all_data = []
    for gender in ['fe', 'me']:
        folder = os.path.join(BASE_PATH, gender)
        if not os.path.isdir(folder):
            continue
        for fn in os.listdir(folder):
            if fn.endswith('_clustered_features.csv'):
                elephant_id = fn.split('_')[0]
                fp = os.path.join(folder, fn)
                df = pd.read_csv(fp)
                df['elephant_id'] = elephant_id
                df['gender'] = gender
                all_data.append(df)
    if not all_data:
        raise ValueError("No data found!")
    combined = pd.concat(all_data, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'])
    return combined

# Load data
df = load_all_clustered_features()

# Ensure output root
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# ------------------- HELPER: Plot Total Distance + Rolling Std -------------------
def plot_distance_and_std(df, title_suffix, filename_prefix, out_dir, color_dist='steelblue', color_std='darkorange'):
    dist = df['total_distance']
    std_roll = dist.rolling(window=ROLLING_WINDOW, min_periods=1).std()

    # 1. Total Distance
    plt.figure(figsize=(14, 5))
    plt.plot(dist.index, dist, linewidth=0.8, color=color_dist)
    plt.title(f'Total Distance – {title_suffix}')
    plt.xlabel('Date')
    plt.ylabel('Total Distance (km)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{filename_prefix}_total_distance.png"), dpi=150)
    plt.close()

    # 2. Rolling Std Dev
    plt.figure(figsize=(14, 5))
    plt.plot(std_roll.index, std_roll, linewidth=1.0, color=color_std)
    plt.fill_between(std_roll.index, std_roll, alpha=0.2, color=color_std)
    plt.title(f'30-Day Rolling Std Dev – {title_suffix}')
    plt.xlabel('Date')
    plt.ylabel('Std Dev of Daily Distance (km)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{filename_prefix}_rolling_std.png"), dpi=150)
    plt.close()

# ------------------- 1. PER ELEPHANT PER YEAR -------------------
print("Generating per-elephant per-year plots...")
for elephant_id in df['elephant_id'].unique():
    ele_df = df[df['elephant_id'] == elephant_id][['date', 'total_distance', 'gender']].copy()
    ele_df['date'] = pd.to_datetime(ele_df['date'])
    ele_df = ele_df.set_index('date').sort_index()
    ele_df = ele_df.asfreq('D', fill_value=np.nan)

    gender = ele_df['gender'].iloc[0] if 'gender' in ele_df.columns and not ele_df['gender'].empty else 'unknown'
    ele_dir = os.path.join(OUTPUT_ROOT, gender, elephant_id)
    os.makedirs(ele_dir, exist_ok=True)

    # Add year
    dist_df = ele_df[['total_distance']].copy()
    dist_df['year'] = dist_df.index.year

    # Per year
    for year in dist_df['year'].unique():
        year_df = dist_df[dist_df['year'] == year]
        plot_distance_and_std(
            df=year_df,
            title_suffix=f"{elephant_id} – {year}",
            filename_prefix=f"ts_{elephant_id}{elephant_id}{year}",
            out_dir=ele_dir
        )

    # ------------------- 2. PER ELEPHANT OVERALL (ALL YEARS) -------------------
    plot_distance_and_std(
        df=dist_df,
        title_suffix=f"{elephant_id} – All Years",
        filename_prefix=f"ts_{elephant_id}_{elephant_id}_all",
        out_dir=ele_dir
    )

# ------------------- 3. PER GENDER OVERALL (ALL ELEPHANTS, ALL YEARS) -------------------
# ------------------- 3. PER GENDER OVERALL (ALL ELEPHANTS, ALL YEARS) -------------------
print("Generating per-gender overall plots...")
for gender in ['fe', 'me']:
    gender_df = df[df['gender'] == gender].copy()
    if gender_df.empty:
        continue

    gender_df['date'] = pd.to_datetime(gender_df['date'])

    # Group by date and average total_distance across all elephants of this gender
    daily_avg = gender_df.groupby('date')['total_distance'].mean().to_frame('total_distance')
    daily_avg = daily_avg.asfreq('D', fill_value=np.nan)  # Now safe: only one value per day

    gender_dir = os.path.join(OUTPUT_ROOT, gender)
    os.makedirs(gender_dir, exist_ok=True)

    plot_distance_and_std(
        df=daily_avg,
        title_suffix=f"All {gender.upper()} Elephants – All Years",
        filename_prefix=f"ts_all_{gender}_all",
        out_dir=gender_dir,
        color_dist='purple',
        color_std='crimson'
    )

print("All plots generated:")
print("  - Per elephant per year")
print("  - Per elephant all years: ts_*_all_total_distance.png")
print("  - Per gender all elephants: ts_all_fe_all_.png, ts_all_me_all_.png")