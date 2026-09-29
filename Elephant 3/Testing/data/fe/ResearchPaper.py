# # ResearchPaper_full_pipeline.py
# import pandas as pd
# import numpy as np
# from pathlib import Path
# import matplotlib.pyplot as plt
# import seaborn as sns
# from scipy.stats import ks_2samp
# from scipy.cluster.hierarchy import linkage, fcluster, dendrogram

# # ------------------- Paths -------------------
# RESULT_ROOT = Path("Research Paper")
# RESULT_ROOT.mkdir(exist_ok=True)
# (RESULT_ROOT / "figures").mkdir(exist_ok=True)

# # ------------------- 1. Load & Clean Data -------------------
# print("Loading data...")
# df = pd.read_csv("results/tables/LA11_with_segments.csv")

# df['datetime'] = pd.to_datetime(df['datetime'])
# df = df.sort_values('datetime').reset_index(drop=True)
# df = df[(df['dt_sec'] > 0) & df['speed'].notna()].copy()

# # Absolute turning angle (tortuosity)
# df['abs_turning_angle'] = np.abs(df['turning_angle'])

# # Persistence velocity (this is what the original BCPA uses)
# df['persistence'] = df['step_length'] * np.cos(np.radians(df['turning_angle']))

# print(f"Data loaded: {len(df):,} locations from {df['datetime'].dt.date.min()} to {df['datetime'].dt.date.max()}")

# # ------------------- 2. Segmentation (fast BCPA-like) -------------------
# print("Running segmentation (BottomUp + l2 cost)...")
# import ruptures as rpt

# signal = df['persistence'].values.reshape(-1, 1)

# # Fast, memory-efficient segmentation
# algo = rpt.BottomUp(model="l2", min_size=15, jump=5)
# algo.fit(signal)

# # Choose number of segments (150–300 works well for elephant data)
# n_segments = 200
# change_points = algo.predict(n_bkps=n_segments - 1)

# # Assign segment IDs
# segments = np.digitize(np.arange(len(df)), change_points[:-1])
# df['new_segment'] = segments + 1

# print(f"Detected {df['new_segment'].nunique()} segments")

# # ------------------- 3. Segment Statistics -------------------
# print("Computing segment statistics...")
# segment_stats = df.groupby('new_segment').agg(
#     start_time=('datetime', 'min'),
#     end_time=('datetime', 'max'),
#     duration_min=('datetime', lambda x: (x.max() - x.min()).total_seconds() / 60),
#     n_points=('datetime', 'count'),
#     speed_mean=('speed', 'mean'),
#     speed_std=('speed', 'std'),
#     turn_mean=('abs_turning_angle', 'mean'),
#     turn_std=('abs_turning_angle', 'std'),
#     persistence_mean=('persistence', 'mean')
# ).round(4)

# segment_stats.to_csv(RESULT_ROOT / "segment_statistics.csv")
# print(f"Segment stats saved → {RESULT_ROOT / 'segment_statistics.csv'}")

# # ------------------- 4. Hierarchical Clustering with KS distance -------------------
# print("Running KS-distance hierarchical clustering...")
# unique_segs = df['new_segment'].unique()
# n = len(unique_segs)
# dist_matrix = np.zeros((n, n))

# for i, s1 in enumerate(unique_segs):
#     d1 = df[df['new_segment'] == s1]
#     speed1 = d1['speed'].values
#     turn1 = d1['abs_turning_angle'].values
#     for j, s2 in enumerate(unique_segs[i+1:], i+1):
#         d2 = df[df['new_segment'] == s2]
#         speed2 = d2['speed'].values
#         turn2 = d2['abs_turning_angle'].values

#         ks_s = ks_2samp(speed1, speed2).statistic
#         ks_t = ks_2samp(turn1, turn2).statistic
#         dist = (ks_s + ks_t) / 2

#         dist_matrix[i, j] = dist_matrix[j, i] = dist

# # Hierarchical clustering (Ward)
# Z = linkage(dist_matrix, method='ward')
# df['behavior_cluster'] = df['new_segment'].map(
#     dict(zip(unique_segs, fcluster(Z, t=3, criterion='maxclust')))
# )

# # ------------------- 5. Label behaviors (as defined in the paper) -------------------
# cluster_means = df.groupby('behavior_cluster').agg(
#     speed_mean=('speed', 'mean'),
#     turn_mean=('abs_turning_angle', 'mean')
# ).sort_values(['speed_mean', 'turn_mean'])

# # Paper definition:
# # - low speed + low turn  → resting
# # - low speed + high turn → foraging
# # - high speed + low turn → walking
# label_map = {
#     cluster_means.index[0]: 'resting',
#     cluster_means.index[1]: 'foraging',
#     cluster_means.index[2]: 'walking'
# }
# df['behavior'] = df['behavior_cluster'].map(label_map)

# cluster_means['behavior'] = cluster_means.index.map(label_map)
# cluster_means.to_csv(RESULT_ROOT / "behavior_cluster_means.csv")
# print("\nBehavior cluster characteristics:")
# print(cluster_means)

# # ------------------- 6. Save Final Results -------------------
# df.to_csv(RESULT_ROOT / "LA11_behavior_classified.csv", index=False)
# df[['datetime', 'Longitude', 'Latitude', 'speed', 'abs_turning_angle',
#     'new_segment', 'behavior_cluster', 'behavior']].to_csv(
#     RESULT_ROOT / "LA11_resegmented.csv", index=False)

# print(f"All results saved in: {RESULT_ROOT.resolve()}")

# # ------------------- 7. Daily Behavior Summary -------------------
# df['date'] = df['datetime'].dt.date
# daily_hours = (df.groupby(['date', 'behavior'])['dt_sec'].sum() / 3600).unstack(fill_value=0)
# daily_hours = daily_hours.reindex(columns=['resting', 'foraging', 'walking'], fill_value=0)
# daily_hours.to_csv(RESULT_ROOT / "daily_behavior_duration_hours.csv")


# # Dendrogram
# plt.figure(figsize=(12, 6))
# dendrogram(Z, truncate_mode='level', p=5)
# plt.title("Hierarchical Clustering Dendrogram (KS distance)")
# plt.xlabel("Segment")
# plt.ylabel("Distance")
# plt.savefig(RESULT_ROOT / "figures/dendrogram.png", dpi=200, bbox_inches='tight')
# plt.close()

# print("All done! Check the 'Research Paper' folder.")



# # ------------------- 4. YEARLY FIGURES -------------------
# df['year'] = df['datetime'].dt.year
# df['date'] = df['datetime'].dt.date

# # Color palette
# palette = {'resting': '#1f77b4', 'foraging': '#ff7f0e', 'walking': '#2ca02c'}

# for year in sorted(df['year'].unique()):
#     print(f"Plotting year {year}...")
#     year_df = df[df['year'] == year].copy()

#     # === 1. Trajectory map for this year ===
#     plt.figure(figsize=(10, 8))
#     sns.scatterplot(data=year_df.sample(frac=0.5, random_state=42),
#                     x='Longitude', y='Latitude',
#                     hue='behavior', palette=palette,
#                     alpha=0.7, s=12, edgecolor='none')
#     plt.title(f"Elephant LA11 – Movement Behavior in {year}", fontsize=16, pad=20)
#     plt.legend(title="Behavior", loc="upper right")
#     plt.xlabel("Longitude")
#     plt.ylabel("Latitude")
#     plt.tight_layout()
#     plt.savefig(FIG_ROOT / f"trajectory_behavior_{year}.png", dpi=300, bbox_inches='tight')
#     plt.close()

#     # === 2. Daily behavior stacked bar for this year ===
#     daily = (year_df.groupby(['date', 'behavior'])['dt_sec'].sum() / 3600).unstack(fill_value=0)
#     daily = daily.reindex(columns=['resting', 'foraging', 'walking'], fill_value=0)

#     plt.figure(figsize=(14, 5))
#     daily.plot(kind='bar', stacked=True, color=[palette[c] for c in daily.columns], width=0.8)
#     plt.title(f"Daily Time Budget – {year}", fontsize=16)
#     plt.ylabel("Hours per day")
#     plt.xlabel("Date")
#     plt.legend(title="Behavior")
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     plt.savefig(FIG_ROOT / f"daily_behavior_stacked_{year}.png", dpi=300, bbox_inches='tight')
#     plt.close()

# # ------------------- 5. Summary Tables -------------------
# daily_all = (df.groupby(['date', 'behavior'])['dt_sec'].sum() / 3600).unstack().fillna(0)
# daily_all = daily_all.reindex(columns=['resting', 'foraging', 'walking'], fill_value=0)
# daily_all.to_csv(RESULT_ROOT / "daily_behavior_duration_hours.csv")

# cluster_means['behavior'] = cluster_means.index.map(label_map)
# cluster_means.to_csv(RESULT_ROOT / "behavior_cluster_means.csv")

# print("\nAll done!")
# print(f"Check folder: {RESULT_ROOT.resolve()}")
# print(f"Yearly figures saved in: {FIG_ROOT.resolve()}")


# "Further Analysis of segmented results"


# group_similar_segments.py
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import seaborn as sns

RESULT_ROOT = Path("Research Paper")
FIG_ROOT = RESULT_ROOT / "figures"
FIG_ROOT.mkdir(exist_ok=True)

# 1. Load the segment statistics you already saved
seg_stats = pd.read_csv(RESULT_ROOT / "segment_statistics.csv")

print(f"Loaded {len(seg_stats)} segments")

# 2. Choose the features that describe movement behavior best
features = [
    'speed_mean', 'speed_std',
    'turn_mean',  'turn_std',
    'duration_min', 'persistence_mean'
]

X = seg_stats[features].copy()

# Clean any infinite or NaN values (shouldn't be any, but just in case)
X = X.replace([np.inf, -np.inf], np.nan).dropna()
seg_stats = seg_stats.loc[X.index].reset_index(drop=True)
X = X.reset_index(drop=True)

# 3. Standardize (very important because duration is in minutes, speed in m/s)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Quick clustering with K-means (3–6 clusters usually enough)
kmeans = KMeans(n_clusters=5, random_state=42, n_init=20)
seg_stats['kmeans_group'] = kmeans.fit_predict(X_scaled)

# 5. Hierarchical clustering + dendrogram (beautiful visualization)
linked = linkage(X_scaled, method='ward')

plt.figure(figsize=(12, 6))
dendrogram(linked, truncate_mode='level', p=5, leaf_rotation=90)
plt.title("Hierarchical Clustering of Segments (using segment statistics)")
plt.xlabel("Segment (or cluster of segments)")
plt.ylabel("Ward distance")
plt.tight_layout()
plt.savefig(FIG_ROOT / "segments_dendrogram_from_statistics.png", dpi=300, bbox_inches='tight')
plt.close()

# Cut the dendrogram into 5 groups
hier_labels = AgglomerativeClustering(n_clusters=5, linkage='ward').fit_predict(X_scaled)
seg_stats['hier_group'] = hier_labels

# 6. Show the mean characteristics of each group
summary_kmeans = seg_stats.groupby('kmeans_group')[features].mean().round(3)
summary_kmeans['n_segments'] = seg_stats.groupby('kmeans_group').size()
print("\nK-means groups (using segment statistics):")
print(summary_kmeans.sort_values(['speed_mean', 'turn_mean']))

summary_hier = seg_stats.groupby('hier_group')[features].mean().round(3)
summary_hier['n_segments'] = seg_stats.groupby('hier_group').size()
print("\nHierarchical groups (using segment statistics):")
print(summary_hier.sort_values(['speed_mean', 'turn_mean']))

# 7. Save everything
seg_stats.to_csv(RESULT_ROOT / "segment_statistics_with_groups.csv", index=False)
summary_kmeans.to_csv(RESULT_ROOT / "kmeans_groups_summary.csv")
summary_hier.to_csv(RESULT_ROOT / "hierarchical_groups_summary.csv")

# 8. Nice visualization of the groups
plt.figure(figsize=(10, 6))
sns.scatterplot(data=seg_stats, x='speed_mean', y='turn_mean',
                hue='kmeans_group', size='duration_min',
                palette='deep', alpha=0.8, sizes=(20, 200))
plt.title("Segment Groups – Speed vs Turning Angle (size = duration)")
plt.xlabel("Mean speed (m/s)")
plt.ylabel("Mean |turning angle| (degrees)")
plt.legend(title="K-means group", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(FIG_ROOT / "segment_groups_speed_vs_turning.png", dpi=300, bbox_inches='tight')
plt.close()

print("\nAll done! Check the new files and plots in 'Research Paper/'")