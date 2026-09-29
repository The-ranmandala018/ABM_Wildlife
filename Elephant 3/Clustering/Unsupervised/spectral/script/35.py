import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.stats import circmean, circstd

# ==========================================================
# HARD-CODED FEATURE SELECTION
# ==========================================================
# Add your specific 33 mobility features here + 2 climate features
# Ensure these names exactly match the generated dataframe columns
SELECTED_FEATURES = [
    'step_sum_08', 'step_sum_09', 'step_sum_10', 'step_sum_11', 'step_sum_12',
    'turn_mean_08', 'turn_mean_09', 'turn_mean_10', 'turn_mean_11', 'turn_mean_12',
    'turn_std_08', 'turn_std_09', 'turn_std_10', 'turn_std_11', 'turn_std_12',
    'nsd_mean_08', 'nsd_mean_09', 'nsd_mean_10', 'nsd_mean_11', 'nsd_mean_12',
    'speed_mean_08', 'speed_mean_09', 'speed_mean_10', 'speed_mean_11', 'speed_mean_12',
    'step_sum_20', 'step_sum_21', 'turn_std_20', 'turn_std_21', 'speed_mean_20', 
    'speed_mean_21', 'nsd_mean_20', 'nsd_mean_21',
    'Humidity', 'Dew_C' # Climate features added to the 35 count
]

# ==========================================================
# PATH SETUP
# ==========================================================
BASE_DIR = os.getcwd()  # Use current working directory to avoid __file__ issues
SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "segments")
RESULTS_DIR = os.path.join(BASE_DIR, "..", "results", "35D_Hardcoded")
CLIMATE_CSV = os.path.join(BASE_DIR, "okaukuejo_daily_2010_2013.csv")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.environ["OMP_NUM_THREADS"] = "1"
eps = 1e-8
MAX_K = 10

def run_spectral_pipeline(csv_path, climate_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # 1. LOAD CLIMATE
    df_clim = pd.read_csv(climate_path)
    df_clim['date'] = pd.to_datetime(df_clim['date'])
    df_clim['month_idx'] = df_clim['date'].dt.strftime('%Y-%m')
    clim_monthly = df_clim.groupby('month_idx').agg({'Humidity': 'mean', 'Dew_C': 'mean'})

    # 2. LOAD MOBILITY
    df = pd.read_csv(csv_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["year"], df["month"], df["hour"] = df["datetime"].dt.year, df["datetime"].dt.month, df["datetime"].dt.hour
    
    # Simple NSD calculation
    first_lon, first_lat = df.iloc[0]['Longitude'], df.iloc[0]['Latitude']
    df['nsd'] = (df['Longitude'] - first_lon)**2 + (df['Latitude'] - first_lat)**2

    df_hourly = df.groupby(["year", "month", "hour"]).agg({
        "step_length": "sum",
        "turning_angle": [lambda x: circmean(x, low=-180, high=180), lambda x: circstd(x, low=-180, high=180)],
        "nsd": "mean", "speed": "mean"
    })
    df_hourly.columns = ['step_sum', 'turn_mean', 'turn_std', 'nsd_mean', 'speed_mean']
    df_hourly = df_hourly.reset_index()

    # 3. CONSTRUCT MATRIX
    metrics = ["step_sum", "turn_mean", "turn_std", "nsd_mean", "speed_mean"]
    rows, month_labels = [], []
    for (y, m), g in df_hourly.groupby(["year", "month"]):
        if len(g) == 24:
            # Flatten 24 hours for each metric
            vals = np.hstack([g[met].values for met in metrics])
            rows.append(vals)
            month_labels.append(f"{y}-{m:02d}")

    col_names = [f"{m}_{h:02d}" for m in metrics for h in range(24)]
    mob_df = pd.DataFrame(rows, columns=col_names, index=month_labels)
    
    # 4. JOIN & SELECT
    full_df = mob_df.join(clim_monthly, how='inner').dropna()
    
    # Validate features exist
    missing = [f for f in SELECTED_FEATURES if f not in full_df.columns]
    if missing:
        raise ValueError(f"The following features are missing from the dataframe: {missing}")
    
    X_35D = full_df[SELECTED_FEATURES]

    # 5. STANDARDIZATION & CLUSTERING
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_35D.values)
    n = X_scaled.shape[0]  # Define n here

    # 6. SPECTRAL CLUSTERING (Sigma Sweep)
    sq_dist = np.sum((X_scaled[:, None, :] - X_scaled[None, :, :]) ** 2, axis=-1)
    sigmas = np.logspace(-1, 1.5, 30)
    gaps_vs_sigma = np.zeros((MAX_K - 1, len(sigmas)))

    for s, sigma in enumerate(sigmas):
        A = np.exp(-sq_dist / (2 * sigma**2))
        np.fill_diagonal(A, 0)
        D = np.sum(A, axis=1)
        if np.any(D < eps): continue
        D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
        L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt
        eigvals = np.sort(np.linalg.eigvalsh(L_sym))
        gaps = np.diff(eigvals)
        for m in range(min(MAX_K - 1, len(gaps) - 1)):
            gaps_vs_sigma[m, s] = gaps[m + 1]

    # ------------------------------------------------------
    # 7 SAVE SIGMA VALUES PER MODE
    # ------------------------------------------------------

    sigma_modes = {}

    for m in range(MAX_K - 1):
        if np.all(gaps_vs_sigma[m] == 0):
            continue

        best_sigma_idx = np.argmax(gaps_vs_sigma[m])
        sigma_modes[f"{m+2}-{m+3}"] = sigmas[best_sigma_idx]

    sigma_df = pd.DataFrame.from_dict(
        sigma_modes, orient="index", columns=["best_sigma"]
    )
    sigma_df.index.name = "eigengap_mode"

    sigma_df.to_csv(
        os.path.join(output_dir, "sigma_per_eigengap_mode_Hourly.csv")
    )

    # ------------------------------------------------------
    # 8. EIGENGAP PLOT
    # ------------------------------------------------------

    plt.figure(figsize=(9, 5))

    for m in range(MAX_K - 1):
        if np.all(gaps_vs_sigma[m] == 0):
            continue
        plt.plot(
            sigmas,
            gaps_vs_sigma[m],
            marker="o",
            label=f"{m+2}-{m+3}"
        )

    plt.xscale("log")
    plt.xlabel("Sigma")
    plt.ylabel("Eigen gap")
    plt.title("Eigen gaps across sigma sweep")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "eigengaps_vs_sigma_Hourly.png"),
        dpi=300
    )
    # Show the plot interactively
    plt.show()
    # Ask for the eigengap mode
    print("Available eigengap modes:", list(sigma_modes.keys()))
    selected_mode = input("Enter the eigengap mode (e.g., 2-3): ").strip()
    if selected_mode not in sigma_modes:
        print(f"Invalid mode: {selected_mode}. Available: {list(sigma_modes.keys())}")
        return
    else:
        best_k = int(selected_mode.split("-")[0])
        best_sigma = sigma_modes[selected_mode]
        print(f"Selected mode: {selected_mode}, k={best_k}, sigma={best_sigma:.4f}")
        # ------------------------------------------------------
        # 9. FINAL CLUSTERING (USING SELECTED MODE)
        # ------------------------------------------------------
        A = np.exp(-sq_dist / (2 * best_sigma**2))
        np.fill_diagonal(A, 0)
        D = np.sum(A, axis=1)
        D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
        L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt
        eigvals, eigvecs = np.linalg.eigh(L_sym)
        idx = np.argsort(eigvals)
        U = eigvecs[:, idx[:best_k]]
        U = U / np.linalg.norm(U, axis=1, keepdims=True)
        labels = KMeans(
            n_clusters=best_k,
            random_state=42,
            n_init="auto"
        ).fit_predict(U)
        clustered = pd.DataFrame({
            "month": full_df.index.tolist(),  # Use full_df.index to match lengths after dropna
            "cluster": labels
        })
        clustered.to_csv(
            os.path.join(output_dir, f"monthly_clusters_{selected_mode}.csv"),
            index=False
        )
        # ------------------------------------------------------
        # 10. SAVE FEATURE MATRICES PER CLUSTER
        # ------------------------------------------------------
        for cluster in np.unique(labels):
            idxs = np.where(labels == cluster)[0]
            cluster_matrix = X_35D.iloc[idxs].values  # Use X_35D for selected features
            np.savetxt(
                os.path.join(output_dir, f"cluster_{cluster}_features_{selected_mode}.csv"),
                cluster_matrix,
                delimiter=","
            )
            print(
                f"Cluster {cluster}: feature matrix shape "
                f"{cluster_matrix.shape}"
            )
        # ------------------------------------------------------
        # 11. CLUSTER AVERAGE PROFILES (UPDATED FOR 120D)
        # ------------------------------------------------------
        df_hourly["month_str"] = (
            df_hourly["year"].astype(str) + "-" +
            df_hourly["month"].astype(str).str.zfill(2)
        )
        merged = df_hourly.merge(
            clustered, left_on="month_str", right_on="month"
        )
        
        for c in range(best_k):
            cd = merged[merged["cluster"] == c]
            if cd.empty:
                continue
            
            # Use the correct aggregated column names
            avg_step = cd.groupby("hour")["step_sum"].mean()
            avg_turn_mean = cd.groupby("hour")["turn_mean"].mean()
            avg_turn_std = cd.groupby("hour")["turn_std"].mean()
            avg_nsd = cd.groupby("hour")["nsd_mean"].mean()
            
            # Create a larger plot to show all movement facets
            plt.figure(figsize=(16, 10))
            
            # Subplot 1: Step Intensity
            plt.subplot(2, 2, 1)
            plt.plot(avg_step.index, avg_step.values, marker="o", color='blue')
            plt.title(f"Cluster {c} – Step Sum (Intensity)")
            plt.ylabel("Meters")
            plt.grid(True)
            
            # Subplot 2: Turning Angle Bias
            plt.subplot(2, 2, 2)
            plt.plot(avg_turn_mean.index, avg_turn_mean.values, marker="o", color='orange')
            plt.title(f"Cluster {c} – Circular Mean Turn")
            plt.ylabel("Degrees")
            plt.grid(True)

            # Subplot 3: Search Complexity (Tortuosity)
            plt.subplot(2, 2, 3)
            plt.plot(avg_turn_std.index, avg_turn_std.values, marker="o", color='red')
            plt.title(f"Cluster {c} – Turn SD (Complexity)")
            plt.ylabel("SD (Degrees)")
            plt.grid(True)

            # Subplot 4: Displacement
            plt.subplot(2, 2, 4)
            plt.plot(avg_nsd.index, avg_nsd.values, marker="o", color='green')
            plt.title(f"Cluster {c} – Mean NSD (Displacement)")
            plt.ylabel("Distance^2")
            plt.grid(True)
            
            plt.suptitle(f"Behavioral Profile for Cluster {c} ({selected_mode})", fontsize=16)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.savefig(
                os.path.join(output_dir, f"cluster_{c}_profiles_120D_{selected_mode}.png"),
                dpi=300
            )
            plt.close()
        

            


# # ==========================================================
# # BATCH PROCESS
# # ==========================================================

# for group in ["fe", "me"]:

#     group_dir = os.path.join(SEGMENTS_DIR, group)
#     result_group_dir = os.path.join(RESULTS_DIR, group)
#     os.makedirs(result_group_dir, exist_ok=True)

#     for file in sorted(os.listdir(group_dir)):

#         if not file.endswith(".csv"):
#             continue

#         file_id = file.split("_")[0]
#         csv_path = os.path.join(group_dir, file)
#         output_dir = os.path.join(result_group_dir, file_id)

#         print(f"\nProcessing: {csv_path}")
#         run_spectral_pipeline(csv_path, CLIMATE_CSV, output_dir)

# ==========================================================
# SINGLE FILE PROCESS (Replaces Batch Process)
# ==========================================================

# 1. Manually specify the file you want to target
TARGET_GROUP = "fe"  # or "me"
TARGET_FILE = "04fe_with_segments.csv" # The exact name of the file

# 2. Define the paths
group_dir = os.path.join(SEGMENTS_DIR, TARGET_GROUP)
csv_path = os.path.join(group_dir, TARGET_FILE)

# 3. Check if the file exists before running
if os.path.exists(csv_path):
    file_id = TARGET_FILE.split("_")[0]
    output_dir = os.path.join(RESULTS_DIR, TARGET_GROUP, file_id)
    
    print(f"\nProcessing Single File: {csv_path}")
    run_spectral_pipeline(csv_path, CLIMATE_CSV, output_dir)
else:
    print(f"Error: The file {csv_path} does not exist.")