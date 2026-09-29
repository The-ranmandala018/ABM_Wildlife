'''Spectral Clustering with stable value from sigma sweep and k means plots for weather data'''

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import calendar

# ===============================
# 1. LOAD AND PREPARE DATA
# ===============================
BASE_DIR = r"D:\Documents\MARC\Elephant\ai4covid_clustering-dev"
CSV_FILE = os.path.join(BASE_DIR, "okaukuejo_daily_2010_2013.csv")
df = pd.read_csv(CSV_FILE)
df['date'] = pd.to_datetime(df['Date'])

df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

# Select relevant features
selected_features = ['Temp_C', 'Precip_mm', 'Pressure_Hg']
df_daily = df[['year', 'month', 'day'] + selected_features]

features = []
month_labels = []

max_days = 31

for (year, month), g in df_daily.groupby(['year', 'month']):
    g = g.sort_values('day')
    
    # Get actual number of days in month
    _, num_days = calendar.monthrange(year, month)
    
    if len(g) != num_days:
        print(f"Warning: Month {year}-{month:02d} has {len(g)} days instead of {num_days}. Skipping or handling accordingly.")
        continue  # Or handle missing days if any, but assuming complete

    month_vec = []
    for feat in selected_features:
        values = g[feat].values
        mean_val = np.mean(values)
        pad_values = np.pad(values, (0, max_days - len(values)), mode='constant', constant_values=mean_val)
        month_vec.append(pad_values)
    
    vec = np.hstack(month_vec)
    
    features.append(vec)
    month_labels.append(f"{year}-{month:02d}")

X = np.array(features)
print("Feature matrix shape:", X.shape)

# ===============================
# 2. STANDARDIZE FEATURES
# ===============================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

n = X_scaled.shape[0]
eps = 1e-8

# Pairwise squared distances
sq_dist = np.sum(
    (X_scaled[:, None, :] - X_scaled[None, :, :]) ** 2,
    axis=-1
)

# ===============================
# 3. SIGMA SWEEP (L_sym)
# ===============================

sigmas = np.logspace(-1, 1.5, 30)  # ~0.1 to ~30
max_k = 10

k_vs_sigma = []
gap_vs_sigma = []

for sigma in sigmas:
    A = np.exp(-sq_dist / (2 * sigma**2))
    np.fill_diagonal(A, 0)

    D = np.sum(A, axis=1)
    if np.any(D < eps):
        k_vs_sigma.append(np.nan)
        gap_vs_sigma.append(0)
        continue

    D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
    L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

    eigvals, _ = np.linalg.eigh(L_sym)

    gaps = np.diff(eigvals[:max_k + 1])
    k_opt = np.argmax(gaps[1:]) + 2  # k >= 2

    k_vs_sigma.append(k_opt)
    gap_vs_sigma.append(gaps[k_opt - 1])

# ===============================
# 4. VISUALIZATION — k vs sigma
# ===============================

plt.figure(figsize=(8, 5))
plt.plot(sigmas, k_vs_sigma, marker='o')
plt.xscale('log')
plt.xlabel("Sigma")
plt.ylabel("Estimated number of clusters (k)")
plt.title("Evolution of cluster count across sigma sweep")
plt.grid(True)
plt.show()

# ===============================
# 5. VISUALIZATION — eigengap strength
# ===============================

plt.figure(figsize=(8, 5))
plt.plot(sigmas, gap_vs_sigma, marker='o')
plt.xscale('log')
plt.xlabel("Sigma")
plt.ylabel("Dominant eigen-gap")
plt.title("Eigen-gap strength across sigma (L_sym)")
plt.grid(True)
plt.show()

# ===============================
# 6. STABILITY-BASED SIGMA SELECTION
# ===============================

window = 3
stability_scores = []
stable_k_per_sigma = []

for i in range(len(sigmas)):
    left = max(0, i - window)
    right = min(len(sigmas), i + window + 1)

    ks = [k_vs_sigma[j] for j in range(left, right) if not np.isnan(k_vs_sigma[j])]
    if len(ks) == 0 or np.isnan(k_vs_sigma[i]):
        stability_scores.append(0)
        stable_k_per_sigma.append(np.nan)
        continue

    most_common_k, count = Counter(ks).most_common(1)[0]
    stability_scores.append(count / len(ks))
    stable_k_per_sigma.append(most_common_k)

plt.figure(figsize=(8, 5))
plt.plot(sigmas, stability_scores, marker='o')
plt.xscale('log')
plt.xlabel("Sigma")
plt.ylabel("Cluster stability score")
plt.title("Stability of k across sigma sweep")
plt.grid(True)
plt.show()

# ===============================
# 7. FINAL SELECTION (STABLE σ for main clusters)
# ===============================

best_idx = np.argmax(stability_scores)
best_sigma = sigmas[best_idx]
best_k = stable_k_per_sigma[best_idx]

print(f"Selected sigma (stable for main): {best_sigma:.4f}")
print(f"Selected number of clusters (k for main): {best_k}")

# ===============================
# 8. SELECTION FOR MICRO CLUSTERS (small sigma with max k)
# ===============================

valid_ks = [k for k in k_vs_sigma if not np.isnan(k)]
if valid_ks:
    micro_k = max(valid_ks)
    micro_idx = min(i for i, k in enumerate(k_vs_sigma) if k == micro_k and not np.isnan(k))  # smallest sigma with max k
    micro_sigma = sigmas[micro_idx]
    print(f"Selected sigma for micro: {micro_sigma:.4f}")
    print(f"Selected number of clusters (k for micro): {micro_k}")
else:
    print("No valid k found for micro clusters.")
    micro_sigma = None
    micro_k = None

# ===============================
# 9. PERFORM CLUSTERING FUNCTION
# ===============================

def perform_clustering(sigma, k, name):
    if sigma is None or k is None or np.isnan(k):
        print(f"Skipping {name} clustering due to invalid parameters.")
        return None, None

    A = np.exp(-sq_dist / (2 * sigma**2))
    np.fill_diagonal(A, 0)

    D = np.sum(A, axis=1)
    if np.any(D < eps):
        print(f"Warning: Some degrees too small for {name} at sigma={sigma:.4f}")
        return None, None

    D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
    L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

    eigvals, eigvecs = np.linalg.eigh(L_sym)
    idx = np.argsort(eigvals)
    eigvecs = eigvecs[:, idx]

    U = eigvecs[:, 1:int(k) + 1]  # Ensure k is int
    U = U / np.linalg.norm(U, axis=1, keepdims=True)

    kmeans = KMeans(n_clusters=int(k), random_state=42, n_init='auto')
    labels = kmeans.fit_predict(U)

    clustered = pd.DataFrame({
        'month': month_labels,
        'cluster': labels
    }).sort_values('cluster')

    clustered.to_csv(f"{name}_monthly_weather_clusters.csv", index=False)

    print(f"\n{name.capitalize()} clustering completed successfully.")
    print(clustered.head())

    return clustered, labels

# ===============================
# 10. EXECUTE CLUSTERING FOR MAIN AND MICRO
# ===============================

main_clustered, main_labels = perform_clustering(best_sigma, best_k, "main")
micro_clustered, micro_labels = perform_clustering(micro_sigma, micro_k, "micro")

# ===============================
# 11. FUNCTION TO ANALYZE AND PLOT CLUSTERS
# ===============================

def analyze_and_plot_clusters(labels, name, k):
    if labels is None:
        return

    # Reconstruct monthly data with labels
    monthly_df = pd.DataFrame({
        'month': month_labels,
        'cluster': labels
    })

    # Merge with df_daily to get features
    df_daily['month_str'] = df_daily['year'].astype(str) + '-' + df_daily['month'].astype(str).str.zfill(2)
    monthly_features = df_daily.merge(monthly_df, left_on='month_str', right_on='month')

    # For each cluster, compute average features per day
    days = np.arange(1, 32)

    for cluster in range(int(k)):
        cluster_data = monthly_features[monthly_features['cluster'] == cluster]

        if cluster_data.empty:
            print(f"No data for {name} cluster {cluster}")
            continue

        avgs = {}
        for feat in selected_features:
            avg_feat = cluster_data.groupby('day')[feat].mean()
            avg_feat = avg_feat.reindex(days)
            avgs[feat] = avg_feat

        # Print summary
        print(f"\n{name.capitalize()} Cluster {cluster} Weather Features (Averages):")
        for feat in selected_features:
            print(f"Daily {feat}:", avgs[feat].values)

        # Dynamic subplot grid based on number of features
        n_features = len(selected_features)
        cols = 3  # You can change to 2 if you want fewer columns
        rows = (n_features + cols - 1) // cols  # Ceiling division for rows needed

        fig, axs = plt.subplots(rows, cols, figsize=(15, 5 * rows))
        
        # Handle case when only 1 row/column
        if n_features == 1:
            axs = [axs]
        else:
            axs = axs.flatten() if n_features > 1 else [axs]

        for i, feat in enumerate(selected_features):
            axs[i].plot(days, avgs[feat], marker='o', color='tab:blue', linewidth=2)
            axs[i].set_title(f"{name.capitalize()} Cluster {cluster} - {feat}")
            axs[i].set_xlabel("Day of Month")
            axs[i].set_ylabel(f"Mean {feat}")
            axs[i].set_xticks(range(1, 32, 5))  # Optional: cleaner x-axis
            axs[i].grid(True, alpha=0.3)

        # Hide any empty subplots (if n_features not multiple of cols)
        for j in range(i + 1, len(axs)):
            axs[j].set_visible(False)

        plt.tight_layout()
        plt.show()

# ===============================
# 12. ANALYZE AND PLOT FOR MAIN AND MICRO
# ===============================

analyze_and_plot_clusters(main_labels, "main", best_k)
analyze_and_plot_clusters(micro_labels, "micro", micro_k)

