import os
import re
import pandas as pd
import folium
from collections import defaultdict

# ----------------------------------------------------------------------
# 1. SETTINGS
# ----------------------------------------------------------------------
IN_FOLDER        = "../Filter_By_Month"         # Folder that contains occ sub-folders
OUT_ROOT         = "../maps_months_hourly_all"  # Where everything will be written
ZOOM_START       = 9
MAP_HEIGHT_PX    = 250

MONTH_COLORS = {
    1: '#008000', 2: '#FF0000', 3: '#0000FF', 4: '#800080',
    5: '#FFA500', 6: '#00FFFF', 7: '#FFFF00', 8: '#FF00FF',
    9: '#A52A2A', 10: '#808080', 11: '#000080', 12: '#FFC0CB'
}
MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Unique colors for 24 hours (using a distinct color palette)
HOUR_COLORS = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF',
    '#FFA500', '#800080', '#008000', '#FFC0CB', '#A52A2A', '#808080',
    '#000080', '#FFD700', '#00CED1', '#FF4500', '#DA70D6', '#228B22',
    '#4682B4', '#ADFF2F', '#DC143C', '#20B2AA', '#9932CC', '#7CFC00'
]

# ----------------------------------------------------------------------
# 2. HELPER
# ----------------------------------------------------------------------
def ensure_folder(p):
    if not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)
        print(f"   Created folder: {p}")

def check_location_consistency(df, month):
    """Check if locations are the same within each hour for the given month."""
    print(f"      Analyzing hourly location consistency for month {month:02d}")
    df['Hour'] = df['Time'].str.split(':').str[0].astype(int)
    hourly_summary = []
    
    for hour in range(24):
        df_hour = df[df['Hour'] == hour]
        if df_hour.empty:
            print(f"         Hour {hour:02d}: No data")
            continue
        unique_locations = df_hour[['Latitude', 'Longitude']].drop_duplicates()
        num_locations = len(unique_locations)
        print(f"         Hour {hour:02d}: {num_locations} unique location(s)")
        hourly_summary.append({
            'Hour': hour,
            'Unique_Locations': num_locations,
            'Sample_Locations': unique_locations.to_dict('records')
        })
    return hourly_summary

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
#   3.1 Walk every occ folder and collect *all* CSV files
# ----------------------------------------------------------------------
elephant_to_year_month = defaultdict(lambda: defaultdict(dict))  # elephant → year → month → df

# regex to extract elephant ID (e.g. a11, a12 …)
ELEPHANT_RE = re.compile(r'^(\d{2}[a-z]{2})')  # first two digits + two letters

for occ in sorted(os.listdir(IN_FOLDER)):
    occ_path = os.path.join(IN_FOLDER, occ)
    if not os.path.isdir(occ_path):
        print(f"   Skipping non-folder: {occ}")
        continue

    print(f"\n--- OCCURRENCE FOLDER: {occ} ---")
    csv_files = [f for f in os.listdir(occ_path) if f.lower().endswith('.csv')]
    if not csv_files:
        print(f"   No *.csv files in {occ_path}")
        continue

    for fname in csv_files:
        print(f"   Examining file: {fname}")

        # ---- 3.2 Extract elephant ID ---------------------------------
        m_id = ELEPHANT_RE.search(fname)
        if not m_id:
            print(f"      → cannot extract elephant ID (need a11/a12 … at start)")
            continue
        elephant_id = m_id.group(1).lower()
        print(f"      → belongs to elephant '{elephant_id}'")

        # ---- 3.3 Parse year-month from the *last* two '_' parts -----
        parts = fname.rsplit('_', 2)
        if len(parts) != 3 or not parts[2].endswith('.csv'):
            print(f"      → cannot parse (need 2 '_' before .csv)")
            continue

        period = parts[2].replace('.csv', '')
        if '-' not in period:
            print(f"      → period part has no '-'")
            continue

        try:
            file_year = int(period.split('-')[0])
            file_month = int(period.split('-')[1])
        except ValueError:
            print(f"      → cannot convert year/month to int")
            continue

        if not (1 <= file_month <= 12):
            print(f"      → month {file_month} out of range")
            continue

        # ---- 3.4 Load CSV -------------------------------------------
        fp = os.path.join(occ_path, fname)
        try:
            df = pd.read_csv(fp)
        except Exception as e:
            print(f"      → FAILED to read CSV: {e}")
            continue

        print(f"      rows before dropna: {len(df)}")
        df.dropna(subset=['Latitude', 'Longitude', 'Time'], inplace=True)
        print(f"      rows after dropna: {len(df)}")
        if df.empty:
            print(f"      → empty after cleaning")
            continue

        # ---- 3.5 Add month column -----------------------------------
        df['Month'] = file_month

        # ---- 3.6 Store -----------------------------------------------
        if file_month in elephant_to_year_month[elephant_id][file_year]:
            elephant_to_year_month[elephant_id][file_year][file_month] = pd.concat(
                [elephant_to_year_month[elephant_id][file_year][file_month], df],
                ignore_index=True)
        else:
            elephant_to_year_month[elephant_id][file_year][file_month] = df

        print(f"      → stored as elephant {elephant_id} | year {file_year} | month {file_month}")

# ----------------------------------------------------------------------
#   3.7 For every elephant and year → build ONE 12-month grid
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
        monthly_html = {}  # month → filename (relative to elephant_out)

        for month in range(1, 13):
            if month not in month_dict:
                print(f"      month {month:02d} → no data")
                continue

            df_m = month_dict[month]
            if df_m.empty:
                print(f"      month {month:02d} → empty after cleaning")
                continue

            # ---- Analyze hourly location consistency ---------------------
            hourly_summary = check_location_consistency(df_m, month)

            lat_c = df_m['Latitude'].mean()
            lon_c = df_m['Longitude'].mean()
            print(f"      month {month:02d} centre [{lat_c:.5f}, {lon_c:.5f}]")

            m = folium.Map(location=[lat_c, lon_c],
                           zoom_start=ZOOM_START,
                           tiles='OpenStreetMap')

            pts = 0
            for _, r in df_m.iterrows():
                if pd.isna(r['Time']) or pd.isna(r['Latitude']) or pd.isna(r['Longitude']):
                    continue
                hour = int(r['Time'].split(':')[0])
                colour = HOUR_COLORS[hour % 24]
                folium.CircleMarker(
                    location=[r['Latitude'], r['Longitude']],
                    radius=5,
                    color=colour,
                    fill=True,
                    fill_color=colour,
                    popup=f"Time: {r['Time']}<br>Month {month} (Hour {hour:02d})"
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
<title>{elephant_id.upper()} {year} – 12-Month Grid (Hourly)</title>
<style>
  body{{font-family:Arial;margin:20px}}
  h1{{text-align:center}}
  .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:1500px;margin:auto}}
  .box{{border:1px solid #aaa;padding:8px;text-align:center;background:#fff}}
  .box h3{{margin:4px 0}}
  iframe{{width:100%;height:{MAP_HEIGHT_PX}px;border:0}}
  .miss{{background:#f8f8f8;color:#999;padding:40px}}
</style></head><body>
<h1>{elephant_id.upper()} – {year} (12-Month Grid, Hourly)</h1>
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

        grid_file = f"{elephant_id.upper()}_{year}_12_Months_Grid_Hourly.html"
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