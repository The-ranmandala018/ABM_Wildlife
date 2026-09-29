# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# """
# Discrete Wavelet Change-Point Detection – Sur et al. (2014)
# Replicates: https://doi.org/10.1016/j.ecoinf.2014.01.007
# Saves all outputs to ./results/
# """

# import os
# import sys
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import geopandas as gpd
# import pywt
# import urllib.request, zipfile, warnings
# from datetime import datetime
# from pathlib import Path

# warnings.filterwarnings("ignore")

# # ------------------------------------------------------------------
# # 0. SETUP: Results directory + logging
# # ------------------------------------------------------------------
# NOW = datetime.now().strftime("%Y-%m-%d_%H-%M")
# RESULT_ROOT = Path("results")
# LOG_DIR = RESULT_ROOT / "logs"
# TABLE_DIR = RESULT_ROOT / "tables"
# FIG_DIR = RESULT_ROOT / "figures"
# CP_DIR = RESULT_ROOT / "change_points"

# for d in (RESULT_ROOT, LOG_DIR, TABLE_DIR, FIG_DIR, CP_DIR):
#     d.mkdir(exist_ok=True)

# log_file = LOG_DIR / f"run_{NOW}.txt"
# def log(msg):
#     print(msg)
#     with open(log_file, "a", encoding="utf-8") as f:
#         f.write(msg + "\n")

# log(f"=== Wavelet analysis started: {datetime.now()} (LK time) ===")

# # ------------------------------------------------------------------
# # 1. DOWNLOAD WORLD BASEMAP (with User-Agent fix)
# # ------------------------------------------------------------------
# def get_world():
#     folder = "naturalearth_lowres"
#     shp = os.path.join(folder, "ne_110m_admin_0_countries.shp")
#     if not os.path.exists(shp):
#         log("Downloading Natural Earth 110m countries …")
#         url = "https://www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"
#         zip_path = "ne_110m_admin_0_countries.zip"

#         req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
#         try:
#             with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as f:
#                 f.write(response.read())
#             with zipfile.ZipFile(zip_path) as z:
#                 z.extractall(folder)
#             os.remove(zip_path)
#             log("Download complete.")
#         except Exception as e:
#             log(f"Download failed: {e}")
#             log("Using empty basemap.")
#             return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
#     return gpd.read_file(shp)

# # ------------------------------------------------------------------
# # 2. LOAD GPS TRACK
# # ------------------------------------------------------------------
# log("Loading 01fe.csv …")
# if not os.path.exists("01fe.csv"):
#     log("ERROR: 01fe.csv not found!")
#     sys.exit(1)

# df = pd.read_csv("01fe.csv")
# df["datetime"] = pd.to_datetime(df["Date"] + " " + df["timeAPM"],
#                                 format="%m/%d/%Y %I:%M:%S %p")
# df = df.sort_values("datetime").reset_index(drop=True)

# gdf = gpd.GeoDataFrame(
#     df,
#     geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
#     crs="EPSG:4326"
# )
# log(f"Loaded {len(gdf)} points from {gdf['datetime'].min()} to {gdf['datetime'].max()}")

# # ------------------------------------------------------------------
# # 3. MOVEMENT PARAMETERS
# # ------------------------------------------------------------------
# R = 6371000
# def haversine(lon1, lat1, lon2, lat2):
#     lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
#     dlon, dlat = lon2 - lon1, lat2 - lat1
#     a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
#     return R * 2 * np.arcsin(np.sqrt(a))

# gdf["step_length"] = 0.0
# for i in range(1, len(gdf)):
#     gdf.loc[i, "step_length"] = haversine(
#         gdf.loc[i-1, "Longitude"], gdf.loc[i-1, "Latitude"],
#         gdf.loc[i, "Longitude"],   gdf.loc[i, "Latitude"]
#     )

# gdf["dt_sec"] = gdf["datetime"].diff().dt.total_seconds().fillna(0)
# gdf["speed"] = gdf["step_length"] / gdf["dt_sec"].replace(0, np.nan)
# gdf["speed"] = gdf["speed"].fillna(0)

# # Residence time (100m radius)
# radius = 100
# gdf["residence_time"] = 0.0
# for i in range(len(gdf)):
#     cur = (gdf.loc[i, "Longitude"], gdf.loc[i, "Latitude"])
#     t = 0
#     for j in range(i + 1, len(gdf)):
#         d = haversine(cur[0], cur[1], gdf.loc[j, "Longitude"], gdf.loc[j, "Latitude"])
#         if d > radius:
#             break
#         t = (gdf.loc[j, "datetime"] - gdf.loc[i, "datetime"]).total_seconds()
#     gdf.loc[i, "residence_time"] = t

# log("Movement parameters computed.")

# # ------------------------------------------------------------------
# # 4. MERGE WEATHER (if available)
# # ------------------------------------------------------------------
# if os.path.exists("okaukuejo_daily_2010_2013.csv"):
#     log("Merging weather data …")
#     weather = pd.read_csv("okaukuejo_daily_2010_2013.csv")
#     weather["Date"] = pd.to_datetime(weather["Date"])
#     gdf["date"] = gdf["datetime"].dt.date
#     gdf = gdf.merge(weather, left_on="date", right_on="Date", how="left")
#     gdf.drop(columns=["Date"], errors="ignore", inplace=True)
# else:
#     log("Weather file not found – skipping.")

# # ------------------------------------------------------------------
# # 5. DWT CHANGE-POINT DETECTION
# # ------------------------------------------------------------------
# signals = {"step_length": gdf["step_length"].values,
#            "residence_time": gdf["residence_time"].values}
# change_idx = set()

# for name, sig in signals.items():
#     log(f"\nDWT on {name} …")
#     coeffs = pywt.wavedec(sig, "db4", level=5)
#     energy = [np.sum(c**2) for c in coeffs[1:]]
#     level = np.argmax(np.abs(np.diff(energy))) + 1
#     log(f"  Strongest scale: level {level}")

#     recon = np.zeros_like(sig)
#     recon[:len(coeffs[level])] = coeffs[level]
#     thr = np.percentile(np.abs(recon), 95)
#     cand = np.where(np.abs(recon) > thr)[0]

#     last = -99
#     for c in cand:
#         if c - last > 3:
#             change_idx.add(c)
#             last = c

# log(f"\nDetected {len(change_idx)} unique change points.")
# with open(CP_DIR / "change_points.txt", "w") as f:
#     f.write("\n".join(map(str, sorted(change_idx))))

# # ------------------------------------------------------------------
# # 6. SEGMENTATION
# # ------------------------------------------------------------------
# gdf["segment"] = 0
# seg = 1
# for i in range(1, len(gdf)):
#     if i in change_idx:
#         seg += 1
#     gdf.loc[i, "segment"] = seg

# # ------------------------------------------------------------------
# # 7. SEGMENT SUMMARY + BEHAVIOR
# # ------------------------------------------------------------------
# summary = []
# for sid, grp in gdf.groupby("segment"):
#     row = {
#         "segment_id": sid,
#         "start": grp["datetime"].min(),
#         "end": grp["datetime"].max(),
#         "n": len(grp),
#         "step_mean": grp["step_length"].mean(),
#         "step_sd": grp["step_length"].std(),
#         "res_mean": grp["residence_time"].mean(),
#         "speed_mean": grp["speed"].mean(),
#         "dist_km": grp["step_length"].sum()/1000,
#         "dur_min": (grp["datetime"].max() - grp["datetime"].min()).total_seconds()/60
#     }
#     if "Temp_C" in grp.columns:
#         row.update({"temp_mean": grp["Temp_C"].mean(), "precip_mm": grp["Precip_mm"].mean()})
#     summary.append(row)

# seg_df = pd.DataFrame(summary)

# def label(row):
#     if row["step_mean"] < 50 and row["res_mean"] > 600: return "Resting"
#     if row["step_mean"] > 200 and row["speed_mean"] > 2: return "Commuting"
#     if row["step_mean"] < 150 and row["res_mean"] > 300: return "Foraging"
#     return "Transitional"

# seg_df["behavior"] = seg_df.apply(label, axis=1)
# log("\nBehavior distribution:")
# log(seg_df["behavior"].value_counts().to_string())

# # ------------------------------------------------------------------
# # 8. SAVE TABLES
# # ------------------------------------------------------------------
# gdf.to_csv(TABLE_DIR / "LA11_with_segments.csv", index=False)
# seg_df.to_csv(TABLE_DIR / "LA11_segment_summary.csv", index=False)
# log("Tables saved.")

# # ------------------------------------------------------------------
# # 9. PLOTS
# # ------------------------------------------------------------------
# world = get_world()

# # Step length
# fig, ax = plt.subplots(figsize=(12,4))
# ax.plot(gdf["datetime"], gdf["step_length"], lw=0.8, color="#1f77b4")
# for cp in change_idx:
#     ax.axvline(gdf.loc[cp, "datetime"], color="red", lw=0.7, ls="--")
# ax.set_ylabel("Step length (m)"); ax.set_title("Step length + Change points")
# fig.savefig(FIG_DIR / "step_length.png", dpi=300, bbox_inches="tight")
# plt.close(fig)

# # Residence time
# fig, ax = plt.subplots(figsize=(12,4))
# ax.plot(gdf["datetime"], gdf["residence_time"], lw=0.8, color="#2ca02c")
# for cp in change_idx:
#     ax.axvline(gdf.loc[cp, "datetime"], color="red", lw=0.7, ls="--")
# ax.set_ylabel("Residence time (s)"); ax.set_title("Residence time + Change points")
# fig.savefig(FIG_DIR / "residence_time.png", dpi=300, bbox_inches="tight")
# plt.close(fig)

# # Map
# fig = plt.figure(figsize=(10,8))
# ax = fig.add_subplot(1,1,1, projection=world.crs)
# world.plot(ax=ax, facecolor="#f0f0f0", edgecolor="gray")
# gdf["beh"] = gdf["segment"].map(seg_df.set_index("segment_id")["behavior"])
# gdf.plot(ax=ax, column="beh", categorical=True, legend=True,
#          markersize=3, alpha=0.7, legend_kwds={"title": "Behavior"})
# ax.set_title("Behavioral Segments – LA11 Gull")
# fig.savefig(FIG_DIR / "behavior_map.png", dpi=300, bbox_inches="tight")
# plt.close(fig)

# log("Figures saved to results/figures/")

# # ------------------------------------------------------------------
# # 10. FINISH
# # ------------------------------------------------------------------
# log("\n=== ANALYSIS COMPLETE ===")
# log(f"Results: {RESULT_ROOT.resolve()}")


#Including turning angle

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Discrete Wavelet Change-Point Detection – Sur et al. (2014)
+ Turning-angle (bearing difference) → DWT change detection
Replicates: https://doi.org/10.1016/j.ecoinf.2014.01.007
Saves all outputs to ./results/
"""

# import os
# import sys
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import geopandas as gpd
# import pywt
# import urllib.request, zipfile, warnings
# from datetime import datetime
# from pathlib import Path

# warnings.filterwarnings("ignore")

# # ------------------------------------------------------------------
# # 0. SETUP: Results directory + logging
# # ------------------------------------------------------------------
# NOW = datetime.now().strftime("%Y-%m-%d_%H-%M")
# RESULT_ROOT = Path("results")
# LOG_DIR = RESULT_ROOT / "logs"
# TABLE_DIR = RESULT_ROOT / "tables"
# FIG_DIR = RESULT_ROOT / "figures"
# CP_DIR = RESULT_ROOT / "change_points"

# for d in (RESULT_ROOT, LOG_DIR, TABLE_DIR, FIG_DIR, CP_DIR):
#     d.mkdir(exist_ok=True)

# log_file = LOG_DIR / f"run_{NOW}.txt"
# def log(msg):
#     print(msg)
#     with open(log_file, "a", encoding="utf-8") as f:
#         f.write(msg + "\n")

# log(f"=== Wavelet analysis (incl. turning angle) started: {datetime.now()} (LK time) ===")

# # ------------------------------------------------------------------
# # 1. DOWNLOAD WORLD BASEMAP (unchanged)
# # ------------------------------------------------------------------
# def get_world():
#     folder = "naturalearth_lowres"
#     shp = os.path.join(folder, "ne_110m_admin_0_countries.shp")
#     if not os.path.exists(shp):
#         log("Downloading Natural Earth 110m countries …")
#         url = "https://www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"
#         zip_path = "ne_110m_admin_0_countries.zip"
#         req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
#         try:
#             with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as f:
#                 f.write(response.read())
#             with zipfile.ZipFile(zip_path) as z:
#                 z.extractall(folder)
#             os.remove(zip_path)
#             log("Download complete.")
#         except Exception as e:
#             log(f"Download failed: {e}")
#             log("Using empty basemap.")
#             return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
#     return gpd.read_file(shp)

# # ------------------------------------------------------------------
# # 2. LOAD GPS TRACK
# # ------------------------------------------------------------------
# log("Loading 01fe.csv …")
# if not os.path.exists("01fe.csv"):
#     log("ERROR: 01fe.csv not found!")
#     sys.exit(1)

# df = pd.read_csv("01fe.csv")
# df["datetime"] = pd.to_datetime(df["Date"] + " " + df["timeAPM"],
#                                 format="%m/%d/%Y %I:%M:%S %p")
# df = df.sort_values("datetime").reset_index(drop=True)

# gdf = gpd.GeoDataFrame(
#     df,
#     geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
#     crs="EPSG:4326"
# )
# log(f"Loaded {len(gdf)} points from {gdf['datetime'].min()} to {gdf['datetime'].max()}")

# # ------------------------------------------------------------------
# # 3. MOVEMENT PARAMETERS (step, speed, residence, **turning angle**)
# # ------------------------------------------------------------------
# R = 6371000
# def haversine(lon1, lat1, lon2, lat2):
#     lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
#     dlon, dlat = lon2 - lon1, lat2 - lat1
#     a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
#     return R * 2 * np.arcsin(np.sqrt(a))

# # ---- step length ----------------------------------------------------
# gdf["step_length"] = 0.0
# for i in range(1, len(gdf)):
#     gdf.loc[i, "step_length"] = haversine(
#         gdf.loc[i-1, "Longitude"], gdf.loc[i-1, "Latitude"],
#         gdf.loc[i, "Longitude"],   gdf.loc[i, "Latitude"]
#     )

# # ---- speed ---------------------------------------------------------
# gdf["dt_sec"] = gdf["datetime"].diff().dt.total_seconds().fillna(0)
# gdf["speed"] = gdf["step_length"] / gdf["dt_sec"].replace(0, np.nan)
# gdf["speed"] = gdf["speed"].fillna(0)

# # ---- residence time (100 m radius) ---------------------------------
# radius = 100
# gdf["residence_time"] = 0.0
# for i in range(len(gdf)):
#     cur = (gdf.loc[i, "Longitude"], gdf.loc[i, "Latitude"])
#     t = 0
#     for j in range(i + 1, len(gdf)):
#         d = haversine(cur[0], cur[1],
#                       gdf.loc[j, "Longitude"], gdf.loc[j, "Latitude"])
#         if d > radius:
#             break
#         t = (gdf.loc[j, "datetime"] - gdf.loc[i, "datetime"]).total_seconds()
#     gdf.loc[i, "residence_time"] = t

# # ---- turning angle (bearing difference) ----------------------------
# def bearing(lon1, lat1, lon2, lat2):
#     """Return bearing in degrees (0-360) from point 1 to point 2."""
#     lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
#     dlon = lon2 - lon1
#     y = np.sin(dlon) * np.cos(lat2)
#     x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
#     brng = np.degrees(np.arctan2(y, x))
#     return (brng + 360) % 360

# gdf["bearing"] = 0.0
# for i in range(1, len(gdf)):
#     gdf.loc[i, "bearing"] = bearing(
#         gdf.loc[i-1, "Longitude"], gdf.loc[i-1, "Latitude"],
#         gdf.loc[i, "Longitude"],   gdf.loc[i, "Latitude"]
#     )

# # Wrapped turning angle (-180° … +180°)
# gdf["turning_angle"] = np.diff(gdf["bearing"], prepend=gdf["bearing"].iloc[0])
# gdf["turning_angle"] = ((gdf["turning_angle"] + 180) % 360) - 180

# log("Movement parameters (incl. turning_angle) computed.")

# # ------------------------------------------------------------------
# # 4. MERGE WEATHER (unchanged)
# # ------------------------------------------------------------------
# if os.path.exists("okaukuejo_daily_2010_2013.csv"):
#     log("Merging weather data …")
#     weather = pd.read_csv("okaukuejo_daily_2010_2013.csv")
#     weather["Date"] = pd.to_datetime(weather["Date"])
#     gdf["date"] = gdf["datetime"].dt.date
#     gdf = gdf.merge(weather, left_on="date", right_on="Date", how="left")
#     gdf.drop(columns=["Date"], errors="ignore", inplace=True)
# else:
#     log("Weather file not found – skipping.")

# # ------------------------------------------------------------------
# # 5. DWT CHANGE-POINT DETECTION (now also on turning_angle)
# # ------------------------------------------------------------------
# signals = {
#     "step_length": gdf["step_length"].values,
#     "residence_time": gdf["residence_time"].values,
#     "turning_angle": gdf["turning_angle"].values
# }
# change_idx = set()

# for name, sig in signals.items():
#     log(f"\nDWT on {name} …")
#     coeffs = pywt.wavedec(sig, "db4", level=5)
#     energy = [np.sum(c**2) for c in coeffs[1:]]
#     level = np.argmax(np.abs(np.diff(energy))) + 1
#     log(f"  Strongest scale: level {level}")

#     recon = np.zeros_like(sig)
#     recon[:len(coeffs[level])] = coeffs[level]
#     thr = np.percentile(np.abs(recon), 95)
#     cand = np.where(np.abs(recon) > thr)[0]

#     last = -99
#     for c in cand:
#         if c - last > 3:          # minimum gap = 3 fixes
#             change_idx.add(c)
#             last = c

# log(f"\nDetected {len(change_idx)} unique change points (step + residence + turn).")
# with open(CP_DIR / "change_points.txt", "w") as f:
#     f.write("\n".join(map(str, sorted(change_idx))))

# # ------------------------------------------------------------------
# # 6. SEGMENTATION (unchanged)
# # ------------------------------------------------------------------
# gdf["segment"] = 0
# seg = 1
# for i in range(1, len(gdf)):
#     if i in change_idx:
#         seg += 1
#     gdf.loc[i, "segment"] = seg

# # ------------------------------------------------------------------
# # 7. SEGMENT SUMMARY + BEHAVIOR (now with turn stats)
# # ------------------------------------------------------------------
# summary = []
# for sid, grp in gdf.groupby("segment"):
#     row = {
#         "segment_id": sid,
#         "start": grp["datetime"].min(),
#         "end": grp["datetime"].max(),
#         "n": len(grp),
#         "step_mean": grp["step_length"].mean(),
#         "step_sd": grp["step_length"].std(),
#         "res_mean": grp["residence_time"].mean(),
#         "speed_mean": grp["speed"].mean(),
#         "turn_mean": grp["turning_angle"].mean(),
#         "turn_sd": grp["turning_angle"].std(),
#         "dist_km": grp["step_length"].sum()/1000,
#         "dur_min": (grp["datetime"].max() - grp["datetime"].min()).total_seconds()/60
#     }
#     if "Temp_C" in grp.columns:
#         row.update({"temp_mean": grp["Temp_C"].mean(),
#                     "precip_mm": grp["Precip_mm"].mean()})
#     summary.append(row)

# seg_df = pd.DataFrame(summary)

# def label(row):
#     """Heuristic behaviour – now uses turning-angle variance."""
#     if row["step_mean"] < 50 and row["res_mean"] > 600:
#         return "Resting"
#     if row["step_mean"] > 200 and row["speed_mean"] > 2 and row["turn_sd"] < 45:
#         return "Commuting"
#     if row["step_mean"] < 150 and row["res_mean"] > 300 and row["turn_sd"] > 90:
#         return "Foraging"
#     return "Transitional"

# seg_df["behavior"] = seg_df.apply(label, axis=1)
# log("\nBehavior distribution (incl. turning angle):")
# log(seg_df["behavior"].value_counts().to_string())

# # ------------------------------------------------------------------
# # 8. SAVE TABLES (now include turning_angle)
# # ------------------------------------------------------------------
# gdf.to_csv(TABLE_DIR / "LA11_with_segments.csv", index=False)
# seg_df.to_csv(TABLE_DIR / "LA11_segment_summary.csv", index=False)
# log("Tables saved (turning_angle column added).")

# # ------------------------------------------------------------------
# # 9. PLOTS (add turning-angle time series)
# # ------------------------------------------------------------------
# world = get_world()

# # Step length
# fig, ax = plt.subplots(figsize=(12,4))
# ax.plot(gdf["datetime"], gdf["step_length"], lw=0.8, color="#1f77b4")
# for cp in change_idx:
#     ax.axvline(gdf.loc[cp, "datetime"], color="red", lw=0.7, ls="--")
# ax.set_ylabel("Step length (m)"); ax.set_title("Step length + Change points")
# fig.savefig(FIG_DIR / "step_length.png", dpi=300, bbox_inches="tight")
# plt.close(fig)

# # Residence time
# fig, ax = plt.subplots(figsize=(12,4))
# ax.plot(gdf["datetime"], gdf["residence_time"], lw=0.8, color="#2ca02c")
# for cp in change_idx:
#     ax.axvline(gdf.loc[cp, "datetime"], color="red", lw=0.7, ls="--")
# ax.set_ylabel("Residence time (s)"); ax.set_title("Residence time + Change points")
# fig.savefig(FIG_DIR / "residence_time.png", dpi=300, bbox_inches="tight")
# plt.close(fig)

# # Turning angle
# fig, ax = plt.subplots(figsize=(12,4))
# ax.plot(gdf["datetime"], gdf["turning_angle"], lw=0.8, color="#d62728")
# for cp in change_idx:
#     ax.axvline(gdf.loc[cp, "datetime"], color="red", lw=0.7, ls="--")
# ax.set_ylabel("Turning angle (°)")
# ax.set_title("Turning angle + Change points")
# fig.savefig(FIG_DIR / "turning_angle.png", dpi=300, bbox_inches="tight")
# plt.close(fig)

# # Map (behaviour)
# fig = plt.figure(figsize=(10,8))
# ax = fig.add_subplot(1,1,1, projection=world.crs)
# world.plot(ax=ax, facecolor="#f0f0f0", edgecolor="gray")
# gdf["beh"] = gdf["segment"].map(seg_df.set_index("segment_id")["behavior"])
# gdf.plot(ax=ax, column="beh", categorical=True, legend=True,
#          markersize=3, alpha=0.7, legend_kwds={"title": "Behavior"})
# ax.set_title("Behavioral Segments – LA11 Gull")
# fig.savefig(FIG_DIR / "behavior_map.png", dpi=300, bbox_inches="tight")
# plt.close(fig)

# log("Figures saved to results/figures/ (incl. turning_angle.png)")

# # ------------------------------------------------------------------
# # 10. FINISH
# # ------------------------------------------------------------------
# log("\n=== ANALYSIS COMPLETE (turning angle integrated) ===")
# log(f"Results: {RESULT_ROOT.resolve()}")



#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HOURLY DIURNAL MOVEMENT – JANUARY 2010
4 × 7-day blocks → 12 plots (3 metrics × 4 weeks)
No change points | X-axis = Date + Hour | Clean & Zoomable
Matches: Sur et al. (2014), Teimouri et al. (2018), Sethi et al. (2025)
"""

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from pathlib import Path
# from datetime import datetime

# # ------------------------------------------------------------------
# # 0. SETUP
# # ------------------------------------------------------------------
# NOW = datetime.now().strftime("%Y-%m-%d_%H-%M")
# RESULT_ROOT = Path("results_hourly")
# FIG_DIR = RESULT_ROOT / "figures"
# TABLE_DIR = RESULT_ROOT / "tables"

# for d in (RESULT_ROOT, FIG_DIR, TABLE_DIR):
#     d.mkdir(exist_ok=True)

# def log(msg):
#     print(msg)

# log(f"=== HOURLY DIURNAL PLOTS – JANUARY 2010 ===")

# # ------------------------------------------------------------------
# # 1. LOAD DATA
# # ------------------------------------------------------------------
# log("Loading LA11_with_segments.csv ...")
# gdf = pd.read_csv("results/tables/LA11_with_segments.csv")
# gdf['datetime'] = pd.to_datetime(gdf['datetime'])

# # Filter: January 2010
# jan2010 = gdf[
#     (gdf['datetime'].dt.year == 2010) &
#     (gdf['datetime'].dt.month == 1)
# ].copy().sort_values('datetime').reset_index(drop=True)

# if len(jan2010) == 0:
#     log("ERROR: No data in January 2010!")
#     exit(1)

# log(f"January 2010: {len(jan2010)} points from {jan2010['datetime'].min()} to {jan2010['datetime'].max()}")

# # ------------------------------------------------------------------
# # 2. SPLIT INTO 4 × 7-DAY BLOCKS
# # ------------------------------------------------------------------
# jan2010['day'] = jan2010['datetime'].dt.day
# weeks = [
#     (1,  7,  "Week 1 (Jan 1–7)"),
#     (8,  14, "Week 2 (Jan 8–14)"),
#     (15, 21, "Week 3 (Jan 15–21)"),
#     (22, 31, "Week 4 (Jan 22–31)")
# ]

# # Save full hourly data
# jan2010.to_csv(TABLE_DIR / "jan2010_hourly_data.csv", index=False)
# log("Saved: jan2010_hourly_data.csv")

# # ------------------------------------------------------------------
# # 3. PLOT FUNCTION: 3 metrics × 4 weeks = 12 plots
# # ------------------------------------------------------------------
# def plot_week(data, week_num, week_label, metric, ylabel, color, ylim=None):
#     plt.figure(figsize=(16, 5))
#     plt.plot(data['datetime'], data[metric], lw=1.2, color=color, label=ylabel)
#     plt.title(f'{ylabel} – January 2010 | {week_label}', fontsize=14, pad=15)
#     plt.ylabel(ylabel)
#     plt.xlabel('Date & Time (Hourly)')
#     if ylim:
#         plt.ylim(ylim)
#     plt.grid(True, alpha=0.3)
#     plt.legend(loc='upper right')
    
#     # Format x-axis: show date + hour
#     ax = plt.gca()
#     ax.xaxis.set_major_formatter(plt.FixedFormatter(
#         data['datetime'].dt.strftime('%b %d %H:%M').tolist()[::max(1, len(data)//20)]
#     ))
#     plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
#     plt.tight_layout()
#     filename = f"jan2010_week{week_num}_{metric}.png"
#     plt.savefig(FIG_DIR / filename, dpi=300, bbox_inches='tight')
#     plt.close()
#     log(f"Saved: {filename}")

# # ------------------------------------------------------------------
# # 4. GENERATE 12 PLOTS
# # ------------------------------------------------------------------
# for w_num, (start_day, end_day, label) in enumerate(weeks, 1):
#     week_data = jan2010[
#         (jan2010['day'] >= start_day) & (jan2010['day'] <= end_day)
#     ].copy()
    
#     if len(week_data) == 0:
#         log(f"Skipping {label} – no data")
#         continue

#     # Step Length
#     plot_week(
#         data=week_data, week_num=w_num, week_label=label,
#         metric='step_length', ylabel='Step Length (m)', color='#1f77b4',
#         ylim=(0, week_data['step_length'].quantile(0.99))
#     )
    
#     # Speed
#     plot_week(
#         data=week_data, week_num=w_num, week_label=label,
#         metric='speed', ylabel='Speed (m/s)', color='#ff7f0e',
#         ylim=(0, week_data['speed'].quantile(0.99))
#     )
    
#     # Turning Angle
#     plot_week(
#         data=week_data, week_num=w_num, week_label=label,
#         metric='turning_angle', ylabel='Turning Angle (°)', color='#d62728',
#         ylim=(-180, 180)
#     )

# # ------------------------------------------------------------------
# # 5. FINISH
# # ------------------------------------------------------------------
# log("\n=== 12 HOURLY PLOTS COMPLETE ===")
# log(f"All figures saved in: {FIG_DIR.resolve()}")
# log("Open PNGs → ZOOM to explore hourly patterns!")
# log("X-axis shows date + hour → ideal for diurnal cycles")


#!/usr/bin/env python
# -*- coding: utf-8 -*-

# """
# FIXED STATISTICAL HOURLY VARIATION – January 2010
# - Kruskal-Wallis + Dunn's for speed/step
# - Manual Rayleigh for turning angle
# - Hourly means ± SEM plots
# - Heatmap for visualization
# No pingouin dependency for Watson-Williams
# """

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from scipy import stats
# from statsmodels.stats.multitest import multipletests
# from pathlib import Path
# from datetime import datetime

# # Manual Rayleigh test (p-value approximation)
# def rayleigh_test(angles_deg):
#     if len(angles_deg) < 3:
#         return {'z': np.nan, 'p_value': np.nan}
#     angles_rad = np.radians(angles_deg)
#     R_bar = np.sqrt(np.mean(np.cos(angles_rad))**2 + np.mean(np.sin(angles_rad))**2)
#     z = len(angles_deg) * R_bar**2
#     p = np.exp(-z)  # Large-sample approximation
#     return {'z': z, 'p_value': p}

# # ------------------------------------------------------------------
# # 0. SETUP
# # ------------------------------------------------------------------
# RESULT_ROOT = Path("results_stats")
# FIG_DIR = RESULT_ROOT / "figures"
# TABLE_DIR = RESULT_ROOT / "tables"
# for d in (RESULT_ROOT, FIG_DIR, TABLE_DIR):
#     d.mkdir(exist_ok=True)

# def log(msg):
#     print(msg)

# log(f"=== FIXED STATISTICAL ANALYSIS – JANUARY 2010 ===")

# # ------------------------------------------------------------------
# # 1. LOAD & FILTER
# # ------------------------------------------------------------------
# log("Loading LA11_with_segments.csv ...")
# df = pd.read_csv("results/tables/LA11_with_segments.csv")  # Update path if needed
# df['datetime'] = pd.to_datetime(df['datetime'])
# jan = df[(df['datetime'].dt.year == 2010) & (df['datetime'].dt.month == 1)].copy()
# jan['hour'] = jan['datetime'].dt.hour
# jan['date'] = jan['datetime'].dt.date

# log(f"January 2010: {len(jan)} fixes")

# # ------------------------------------------------------------------
# # 2. HOURLY SUMMARY STATS
# # ------------------------------------------------------------------
# hourly = jan.groupby('hour').agg(
#     speed_mean=('speed', 'mean'),
#     speed_sem=('speed', lambda x: x.sem()),
#     step_mean=('step_length', 'mean'),
#     step_sem=('step_length', lambda x: x.sem()),
#     turn_mean=('turning_angle', 'mean'),
#     n=('speed', 'count')
# ).reset_index()

# # Circular mean for turning angle (manual)
# hourly['turn_circmean'] = 0.0
# for h in hourly['hour']:
#     angles = jan[jan['hour'] == h]['turning_angle'].values
#     if len(angles) > 0:
#         angles_rad = np.radians(angles)
#         circ_mean_rad = np.arctan2(np.mean(np.sin(angles_rad)), np.mean(np.cos(angles_rad)))
#         hourly.loc[hourly['hour'] == h, 'turn_circmean'] = np.degrees(circ_mean_rad)

# hourly.to_csv(TABLE_DIR / "jan2010_hourly_stats.csv", index=False)

# # ------------------------------------------------------------------
# # 3. PLOT: Hourly Means ± SEM (3 subplots)
# # ------------------------------------------------------------------
# fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# # Speed
# axes[0].errorbar(hourly['hour'], hourly['speed_mean'], yerr=hourly['speed_sem'],
#                  fmt='o-', capsize=5, color='#ff7f0e', label='Speed ± SEM')
# axes[0].set_ylabel('Speed (m/s)')
# axes[0].set_title('Hourly Speed Variation – January 2010')
# axes[0].grid(True, alpha=0.3)

# # Step Length
# axes[1].errorbar(hourly['hour'], hourly['step_mean'], yerr=hourly['step_sem'],
#                  fmt='s-', capsize=5, color='#1f77b4', label='Step Length ± SEM')
# axes[1].set_ylabel('Step Length (m)')
# axes[1].set_title('Hourly Step Length Variation')
# axes[1].grid(True, alpha=0.3)

# # Turning Angle (Circular Mean)
# axes[2].plot(hourly['hour'], hourly['turn_circmean'], 'd-', color='#d62728', label='Circular Mean')
# axes[2].set_ylabel('Turning Angle (°)')
# axes[2].set_xlabel('Hour of Day')
# axes[2].set_title('Hourly Turning Direction (Circular Mean)')
# axes[2].set_ylim(-180, 180)
# axes[2].grid(True, alpha=0.3)

# plt.tight_layout()
# plt.savefig(FIG_DIR / "jan2010_hourly_trends.png", dpi=300, bbox_inches='tight')
# plt.close()
# log("Saved: jan2010_hourly_trends.png")

# # ------------------------------------------------------------------
# # 4. KRUSKAL-WALLIS (Speed & Step Length)
# # ------------------------------------------------------------------
# # Collect groups (skip empty hours)
# speed_groups = [group['speed'].dropna().values for _, group in jan.groupby('hour') if len(group['speed'].dropna()) > 0]
# step_groups = [group['step_length'].dropna().values for _, group in jan.groupby('hour') if len(group['step_length'].dropna()) > 0]

# kw_speed = stats.kruskal(*speed_groups)
# kw_step = stats.kruskal(*step_groups)

# log(f"Kruskal-Wallis Speed: H={kw_speed.statistic:.2f}, p={kw_speed.pvalue:.4f}")
# log(f"Kruskal-Wallis Step: H={kw_step.statistic:.2f}, p={kw_step.pvalue:.4f}")

# # ------------------------------------------------------------------
# # 5. RAYLEIGH TEST (Turning Angle per Hour)
# # ------------------------------------------------------------------
# rayleigh = []
# for h, group in jan.groupby('hour'):
#     if len(group['turning_angle'].dropna()) > 0:
#         result = rayleigh_test(group['turning_angle'].dropna())
#         result['hour'] = h
#         rayleigh.append(result)

# rayleigh_df = pd.DataFrame(rayleigh)
# rayleigh_df.to_csv(TABLE_DIR / "rayleigh_turning.csv", index=False)
# log("Rayleigh Test (Turning Angle):")
# log(rayleigh_df[['hour', 'z', 'p_value']].round(3).to_string(index=False))

# # ------------------------------------------------------------------
# # 6. HEATMAP: Speed by Hour × Day
# # ------------------------------------------------------------------
# pivot = jan.pivot_table(values='speed', index='date', columns='hour', aggfunc='mean', fill_value=0)
# plt.figure(figsize=(14, 8))
# sns.heatmap(pivot, cmap="viridis", cbar_kws={'label': 'Mean Speed (m/s)'})
# plt.title('Daily Speed Pattern – January 2010')
# plt.xlabel('Hour of Day')
# plt.ylabel('Date')
# plt.tight_layout()
# plt.savefig(FIG_DIR / "jan2010_speed_heatmap.png", dpi=300, bbox_inches='tight')
# plt.close()
# log("Saved: jan2010_speed_heatmap.png")

# # ------------------------------------------------------------------
# # 7. SUMMARY TABLE
# # ------------------------------------------------------------------
# summary = pd.DataFrame({
#     'Test': ['Kruskal-Wallis (Speed)', 'Kruskal-Wallis (Step)', 'Rayleigh (Avg Turn)'],
#     'Statistic': [kw_speed.statistic, kw_step.statistic, rayleigh_df['z'].mean()],
#     'p_value': [kw_speed.pvalue, kw_step.pvalue, rayleigh_df['p_value'].mean()],
#     'Significant': [kw_speed.pvalue < 0.05, kw_step.pvalue < 0.05, rayleigh_df['p_value'].mean() < 0.05]
# })
# summary.to_csv(TABLE_DIR / "statistical_summary.csv", index=False)
# log("\n=== STATISTICAL SUMMARY ===")
# log(summary.to_string(index=False))


"""
HOURLY TRENDS PER MONTH – Speed, Step Length, Turning Angle
One plot per month | 3 subplots | Mean ± SEM | No heatmaps
Replicates: Sur et al. (2014), Teimouri et al. (2018), Sethi et al. (2025)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------
# 0. SETUP
# ------------------------------------------------------------------
RESULT_ROOT = Path("results_hourly_monthly")
FIG_DIR = RESULT_ROOT / "figures"
TABLE_DIR = RESULT_ROOT / "tables"
for d in (RESULT_ROOT, FIG_DIR, TABLE_DIR):
    d.mkdir(exist_ok=True)

def log(msg):
    print(msg)

log(f"=== HOURLY TRENDS PER MONTH – {datetime.now().strftime('%Y-%m-%d %H:%M')} LK ===")

# ------------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------------
log("Loading LA11_with_segments.csv ...")
df = pd.read_csv("results/tables/LA11_with_segments.csv")
df['datetime'] = pd.to_datetime(df['datetime'])
df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['hour'] = df['datetime'].dt.hour
df['year_month'] = df['datetime'].dt.strftime('%Y-%m')

log(f"Data: {len(df):,} points from {df['datetime'].min().date()} to {df['datetime'].max().date()}")

# ------------------------------------------------------------------
# 2. COMPUTE CIRCULAR MEAN (Turning Angle)
# ------------------------------------------------------------------
def circular_mean(angles_deg):
    if len(angles_deg) == 0:
        return np.nan
    rad = np.radians(angles_deg)
    return np.degrees(np.arctan2(np.mean(np.sin(rad)), np.mean(np.cos(rad))))

# ------------------------------------------------------------------
# 3. LOOP OVER EACH MONTH
# ------------------------------------------------------------------
all_stats = []

for ym, group in df.groupby('year_month'):
    if len(group) < 50:  # Skip months with too few points
        log(f"Skipping {ym} (n={len(group)} < 50)")
        continue

    log(f"Processing {ym} (n={len(group)})")

    # Hourly stats
    hourly = group.groupby('hour').agg(
        speed_mean=('speed', 'mean'),
        speed_sem=('speed', lambda x: x.sem()),
        step_mean=('step_length', 'mean'),
        step_sem=('step_length', lambda x: x.sem()),
        turn_circmean=('turning_angle', circular_mean),
        n=('speed', 'count')
    ).reset_index()

    hourly['year_month'] = ym
    all_stats.append(hourly)

    # ------------------------------------------------------------------
    # 4. PLOT: 3 subplots (Speed, Step, Turn)
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

    # Speed
    axes[0].errorbar(hourly['hour'], hourly['speed_mean'], yerr=hourly['speed_sem'],
                     fmt='o-', capsize=4, color='#ff7f0e', label='Speed ± SEM')
    axes[0].set_ylabel('Speed (m/s)')
    axes[0].set_title(f'{ym} – Hourly Movement Patterns')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    # Step Length
    axes[1].errorbar(hourly['hour'], hourly['step_mean'], yerr=hourly['step_sem'],
                     fmt='s-', capsize=4, color='#1f77b4', label='Step Length ± SEM')
    axes[1].set_ylabel('Step Length (m)')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    # Turning Angle (Circular Mean)
    axes[2].plot(hourly['hour'], hourly['turn_circmean'], 'd-', color='#d62728', label='Circular Mean')
    axes[2].set_ylabel('Turning Angle (°)')
    axes[2].set_xlabel('Hour of Day')
    axes[2].set_ylim(-180, 180)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    plt.tight_layout()
    plt.savefig(FIG_DIR / f"{ym}_hourly_trends.png", dpi=300, bbox_inches='tight')
    plt.close()

    log(f"Saved: {ym}_hourly_trends.png")

# ------------------------------------------------------------------
# 5. SAVE ALL STATS
# ------------------------------------------------------------------
if all_stats:
    full_stats = pd.concat(all_stats, ignore_index=True)
    full_stats.to_csv(TABLE_DIR / "monthly_hourly_stats.csv", index=False)
    log(f"All monthly stats saved → {TABLE_DIR / 'monthly_hourly_stats.csv'}")

# ------------------------------------------------------------------
# 6. FINISH
# ------------------------------------------------------------------
log("\n=== ALL MONTHLY HOURLY TRENDS COMPLETE ===")
log(f"Figures: {FIG_DIR.resolve()}")
log("Each plot = 1 month, 3 metrics, hourly mean ± SEM")
log("Ready for Ecological Informatics submission!")

