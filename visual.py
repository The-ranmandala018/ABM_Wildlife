import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================================
# 1. LOAD DATA (robust path handling)
# ==========================================================

base_dir = os.path.dirname(os.path.abspath(__file__))

summary_path = os.path.join(base_dir, '../results/PCASpectral/fe/01fe/Summary.xlsx')
original_features_path = os.path.join(base_dir, '../results/120D/fe/01fe/feature_matrix_for_clustering.csv')

print("Summary path:", summary_path)
print("Exists:", os.path.exists(summary_path))

print("Feature path:", original_features_path)
print("Exists:", os.path.exists(original_features_path))

summary_df = pd.read_excel(summary_path)
df_orig = pd.read_csv(original_features_path, index_col=0)

# ==========================================================
# 2. SELECT CLUSTER MODE
# ==========================================================

target_col = 'cluster_2'

# Ensure 'month' type matches index
summary_df['month'] = summary_df['month'].astype(str)
df_orig.index = df_orig.index.astype(str)

# Merge
df_combined = df_orig.merge(
    summary_df[['month', target_col]],
    left_index=True,
    right_on='month'
)

print("\nCombined shape:", df_combined.shape)

# ==========================================================
# 3. CALCULATE MEAN FEATURE PER CLUSTER (FIXED)
# ==========================================================

# Keep only numeric columns
df_numeric = df_combined.select_dtypes(include=[np.number])

# Group by cluster
cluster_means = df_numeric.groupby(df_combined[target_col]).mean()

print("Cluster means shape:", cluster_means.shape)

# ==========================================================
# 4. VISUALIZE 24-HOUR MOBILITY PROFILES
# ==========================================================

metrics = ["step_sum", "turn_mean", "turn_std", "nsd_mean", "speed_mean"]

plt.figure(figsize=(15, 10))

for i, metric in enumerate(metrics):
    plt.subplot(len(metrics), 1, i + 1)

    # Get and SORT columns correctly (hour order 0–23)
    cols = sorted(
        [c for c in cluster_means.columns if c.startswith(metric)],
        key=lambda x: int(x.split('_')[-1]) if x.split('_')[-1].isdigit() else -1
    )

    if len(cols) == 0:
        print(f"Warning: No columns found for {metric}")
        continue

    for cluster in cluster_means.index:
        plt.plot(
            range(len(cols)),
            cluster_means.loc[cluster, cols],
            label=f'Cluster {cluster}',
            marker='o'
        )

    plt.title(f'24-Hour Behavioral Profile: {metric}')
    plt.ylabel('Standardized Value')
    plt.xticks(range(len(cols)))
    plt.legend()

plt.tight_layout()
plt.savefig(os.path.join(base_dir, 'cluster_mobility_profiles.png'), dpi=300)
plt.show()

# ==========================================================
# 5. HEATMAP OF ALL FEATURES
# ==========================================================

plt.figure(figsize=(20, 8))

sns.heatmap(cluster_means, cmap='RdBu_r', center=0)

plt.title(f'Cluster Feature Matrix (Mode: {target_col})')
plt.xlabel('120D Features')
plt.ylabel('Cluster ID')

plt.tight_layout()
plt.savefig(os.path.join(base_dir, 'cluster_heatmap.png'), dpi=300)

plt.show()