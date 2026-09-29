import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. LOAD DATA (Adjust paths to your structure)


base_dir = os.path.dirname(os.path.abspath(__file__))
summary_path = os.path.join(base_dir, '../results/PCASpectral/fe/01fe/Summary.xlsx')

summary_df = pd.read_excel(summary_path)

original_features_path = "../results/120D/fe/01fe/feature_matrix_for_clustering.csv"
df_orig = pd.read_csv(original_features_path, index_col=0)

# 2. SELECT A CLUSTERING MODE TO ANALYZE (e.g., cluster_4)
target_col = 'cluster_4'
df_combined = df_orig.merge(summary_df[['month', target_col]], 
                           left_index=True, right_on='month')

# 3. CALCULATE MEAN FEATURE PER CLUSTER
# We group by the cluster and calculate the average for each of the 120D features
cluster_means = df_combined.groupby(target_col).mean().drop(columns=['month'])

# 4. VISUALIZE MOBILITY "FINGERPRINTS"
# To make it readable, we'll plot the average 24-hour profile for one specific metric (e.g., step_sum)
metrics = ["step_sum", "turn_mean", "turn_std", "nsd_mean", "speed_mean"]

plt.figure(figsize=(15, 10))
for i, metric in enumerate(metrics):
    plt.subplot(len(metrics), 1, i+1)
    
    # Filter columns that belong to this metric (e.g., step_sum_0 to step_sum_23)
    cols = [c for c in cluster_means.columns if c.startswith(metric)]
    
    for cluster in cluster_means.index:
        plt.plot(range(24), cluster_means.loc[cluster, cols], label=f'Cluster {cluster}', marker='o')
    
    plt.title(f'24-Hour Behavioral Profile: {metric}')
    plt.ylabel('Standardized Value')
    plt.xticks(range(24))
    plt.legend()

plt.tight_layout()
plt.savefig('cluster_mobility_profiles.png', dpi=300)
plt.show()

# 5. HEATMAP OF ALL FEATURES
plt.figure(figsize=(20, 8))
sns.heatmap(cluster_means, cmap='RdBu_r', center=0)
plt.title(f'Cluster Feature Matrix (Mode: {target_col})')
plt.xlabel('120D Features')
plt.ylabel('Cluster ID')
plt.tight_layout()
plt.savefig('cluster_heatmap.png', dpi=300)