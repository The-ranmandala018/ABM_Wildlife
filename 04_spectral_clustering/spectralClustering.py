# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans

# # ==========================================================
# # PATH SETUP
# # ==========================================================

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "segments")
# RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")

# os.makedirs(RESULTS_DIR, exist_ok=True)

# # Silence MKL warning on Windows
# os.environ["OMP_NUM_THREADS"] = "1"

# eps = 1e-8
# MAX_K = 10

# # ==========================================================
# #  SPECTRAL CLUSTERING PIPELINE
# # ==========================================================

# def run_spectral_pipeline(csv_path, output_dir):

#     os.makedirs(output_dir, exist_ok=True)

#     # ------------------------------------------------------
#     # 1. LOAD DATA
#     # ------------------------------------------------------

#     df = pd.read_csv(csv_path)
#     df["datetime"] = pd.to_datetime(df["datetime"])

#     df["year"] = df["datetime"].dt.year
#     df["month"] = df["datetime"].dt.month
#     df["hour"] = df["datetime"].dt.hour

#     # Aggregate hourly mobility per month
#     df_hourly = (
#         df.groupby(["year", "month", "hour"])
#           .agg({
#               "step_length": "sum",
#               "turning_angle": "mean"
#           })
#           .reset_index()
#     )

#     # ------------------------------------------------------
#     # 2. BUILD FEATURE MATRIX (48-D)
#     # ------------------------------------------------------
#     # x_i = [24 hourly step-lengths, 24 hourly turning angles]

#     features = []
#     month_labels = []

#     for (year, month), g in df_hourly.groupby(["year", "month"]):
#         g = g.sort_values("hour")

#         if len(g) != 24:
#             continue  # skip incomplete months

#         x_i = np.hstack([
#             g["step_length"].values,      # 24
#             g["turning_angle"].values     # 24
#         ])  # → 48-D

#         features.append(x_i)
#         month_labels.append(f"{year}-{month:02d}")

#     X = np.array(features)

#     if X.shape[0] < 3:
#         print(f"Skipping {os.path.basename(csv_path)} (too few valid months)")
#         return

#     # ------------------------------------------------------
#     # 3. STANDARDIZATION
#     # ------------------------------------------------------

#     X_scaled = StandardScaler().fit_transform(X)
#     n = X_scaled.shape[0]

#     # Pairwise squared distances
#     sq_dist = np.sum(
#         (X_scaled[:, None, :] - X_scaled[None, :, :]) ** 2,
#         axis=-1
#     )

#     # ------------------------------------------------------
#     # 4. SIGMA SWEEP (EIGENGAP ANALYSIS)
#     # ------------------------------------------------------

#     sigmas = np.logspace(-1, 1.5, 30)
#     num_modes = MAX_K - 1

#     gaps_vs_sigma = np.zeros((num_modes, len(sigmas)))

#     for s, sigma in enumerate(sigmas):

#         # Gaussian similarity (self-similarity = 0)
#         A = np.exp(-sq_dist / (2 * sigma**2))
#         np.fill_diagonal(A, 0)

#         D = np.sum(A, axis=1)
#         if np.any(D < eps):
#             continue

#         D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#         L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

#         eigvals = np.sort(np.linalg.eigvalsh(L_sym))
#         gaps = np.diff(eigvals)

#         max_valid_modes = min(num_modes, len(gaps) - 1)
#         for m in range(max_valid_modes):
#             gaps_vs_sigma[m, s] = gaps[m + 1]

#     # ------------------------------------------------------
#     # 5. EIGENGAP PLOT (MATCHES YOUR FIGURE)
#     # ------------------------------------------------------

#     plt.figure(figsize=(9, 5))

#     for m in range(num_modes):
#         if np.all(gaps_vs_sigma[m] == 0):
#             continue

#         plt.plot(
#             sigmas,
#             gaps_vs_sigma[m],
#             marker="o",
#             linewidth=1.5,
#             label=f"{m+2}{m+3}"
#         )

#     plt.xscale("log")
#     plt.xlabel("Sigma")
#     plt.ylabel("Eigen gap")
#     plt.title("Eigen gaps across sigma sweep for different modes")
#     plt.grid(True, alpha=0.3)
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(
#         os.path.join(output_dir, "eigengaps_vs_sigma_modes.png"),
#         dpi=300
#     )
#     plt.close()

#     # ------------------------------------------------------
#     # 6. SELECT PROMINENT MODE & DOMINANT SIGMA
#     # ------------------------------------------------------

#     idx = np.nanargmax(gaps_vs_sigma)
#     mode_idx, sigma_idx = np.unravel_index(idx, gaps_vs_sigma.shape)

#     best_k = mode_idx + 2
#     best_sigma = sigmas[sigma_idx]

#     print(
#         f"Selected k={best_k}, sigma={best_sigma:.4f} "
#         f"for {os.path.basename(csv_path)}"
#     )

#     # ------------------------------------------------------
#     # 7. FINAL SPECTRAL CLUSTERING
#     # ------------------------------------------------------

#     A = np.exp(-sq_dist / (2 * best_sigma**2))
#     np.fill_diagonal(A, 0)

#     D = np.sum(A, axis=1)
#     D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#     L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

#     eigvals, eigvecs = np.linalg.eigh(L_sym)
#     idx = np.argsort(eigvals)

#     U = eigvecs[:, idx[:best_k]]
#     U = U / np.linalg.norm(U, axis=1, keepdims=True)

#     labels = KMeans(
#         n_clusters=best_k,
#         random_state=42,
#         n_init="auto"
#     ).fit_predict(U)

#     clustered = pd.DataFrame({
#         "month": month_labels,
#         "cluster": labels
#     })

#     clustered.to_csv(
#         os.path.join(output_dir, "monthly_clusters.csv"),
#         index=False
#     )

#     # ------------------------------------------------------
#     # 8. CLUSTER AVERAGE PROFILES
#     # ------------------------------------------------------

#     df_hourly["month_str"] = (
#         df_hourly["year"].astype(str)
#         + "-"
#         + df_hourly["month"].astype(str).str.zfill(2)
#     )

#     merged = df_hourly.merge(
#         clustered,
#         left_on="month_str",
#         right_on="month"
#     )

#     for c in range(best_k):

#         cd = merged[merged["cluster"] == c]
#         if cd.empty:
#             continue

#         avg_step = cd.groupby("hour")["step_length"].mean()
#         avg_turn = cd.groupby("hour")["turning_angle"].mean()

#         plt.figure(figsize=(12, 5))

#         plt.subplot(1, 2, 1)
#         plt.plot(avg_step.index, avg_step.values, marker="o")
#         plt.xlabel("Hour")
#         plt.ylabel("Mean step length")
#         plt.title(f"Cluster {c} – Step length")
#         plt.grid(True)

#         plt.subplot(1, 2, 2)
#         plt.plot(avg_turn.index, avg_turn.values, marker="o")
#         plt.xlabel("Hour")
#         plt.ylabel("Mean turning angle")
#         plt.title(f"Cluster {c} – Turning angle")
#         plt.grid(True)

#         plt.tight_layout()
#         plt.savefig(
#             os.path.join(output_dir, f"cluster_{c}_profiles.png"),
#             dpi=300
#         )
#         plt.close()


# # ==========================================================
# # BATCH PROCESS fe / me
# # ==========================================================

# for group in ["fe", "me"]:

#     group_dir = os.path.join(SEGMENTS_DIR, group)
#     result_group_dir = os.path.join(RESULTS_DIR, group)
#     os.makedirs(result_group_dir, exist_ok=True)

#     for file in sorted(os.listdir(group_dir)):

#         if not file.endswith(".csv"):
#             continue

#         file_id = file.split("_")[0]  # e.g., 01fe, 02me
#         csv_path = os.path.join(group_dir, file)
#         output_dir = os.path.join(result_group_dir, file_id)

#         print(f"\nProcessing: {csv_path}")
#         run_spectral_pipeline(csv_path, output_dir)

'''Largest Sigma '''

# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans

# # ==========================================================
# # PATH SETUP
# # ==========================================================

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "segments")
# RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")

# os.makedirs(RESULTS_DIR, exist_ok=True)

# os.environ["OMP_NUM_THREADS"] = "1"

# eps = 1e-8
# MAX_K = 10

# # ==========================================================
# # CORE PIPELINE
# # ==========================================================

# def run_spectral_pipeline(csv_path, output_dir):

#     os.makedirs(output_dir, exist_ok=True)

#     # ------------------------------------------------------
#     # 1. LOAD DATA
#     # ------------------------------------------------------

#     df = pd.read_csv(csv_path)
#     df["datetime"] = pd.to_datetime(df["datetime"])

#     df["year"] = df["datetime"].dt.year
#     df["month"] = df["datetime"].dt.month
#     df["hour"] = df["datetime"].dt.hour

#     df_hourly = (
#         df.groupby(["year", "month", "hour"])
#           .agg({
#               "step_length": "sum",
#               "turning_angle": "mean"
#           })
#           .reset_index()
#     )

#     # ------------------------------------------------------
#     # 2. BUILD 48-D FEATURE MATRIX
#     # ------------------------------------------------------

#     features = []
#     month_labels = []

#     for (year, month), g in df_hourly.groupby(["year", "month"]):
#         g = g.sort_values("hour")

#         if len(g) != 24:
#             continue

#         x_i = np.hstack([
#             g["step_length"].values,
#             g["turning_angle"].values
#         ])

#         features.append(x_i)
#         month_labels.append(f"{year}-{month:02d}")

#     X = np.array(features)

#     if X.shape[0] < 3:
#         print(f"Skipping {os.path.basename(csv_path)} (too few months)")
#         return

#     # ------------------------------------------------------
#     # 3. STANDARDIZATION
#     # ------------------------------------------------------

#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)
#     n = X_scaled.shape[0]

#     sq_dist = np.sum(
#         (X_scaled[:, None, :] - X_scaled[None, :, :]) ** 2,
#         axis=-1
#     )

#     # ------------------------------------------------------
#     # 4. SIGMA SWEEP + EIGENGAPS
#     # ------------------------------------------------------

#     sigmas = np.logspace(-1, 1.5, 30)
#     num_modes = MAX_K - 1
#     gaps_vs_sigma = np.zeros((num_modes, len(sigmas)))

#     for s, sigma in enumerate(sigmas):

#         A = np.exp(-sq_dist / (2 * sigma**2))
#         np.fill_diagonal(A, 0)

#         D = np.sum(A, axis=1)
#         if np.any(D < eps):
#             continue

#         D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#         L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

#         eigvals = np.sort(np.linalg.eigvalsh(L_sym))
#         gaps = np.diff(eigvals)

#         for m in range(min(num_modes, len(gaps) - 1)):
#             gaps_vs_sigma[m, s] = gaps[m + 1]

#     # ------------------------------------------------------
#     # 5. SAVE SIGMA VALUES PER MODE
#     # ------------------------------------------------------

#     sigma_modes = {}

#     for m in range(num_modes):
#         if np.all(gaps_vs_sigma[m] == 0):
#             continue

#         best_sigma_idx = np.argmax(gaps_vs_sigma[m])
#         sigma_modes[f"{m+2}-{m+3}"] = sigmas[best_sigma_idx]

#     sigma_df = pd.DataFrame.from_dict(
#         sigma_modes, orient="index", columns=["best_sigma"]
#     )
#     sigma_df.index.name = "eigengap_mode"

#     sigma_df.to_csv(
#         os.path.join(output_dir, "sigma_per_eigengap_mode.csv")
#     )

#     # ------------------------------------------------------
#     # 6. EIGENGAP PLOT
#     # ------------------------------------------------------

#     plt.figure(figsize=(9, 5))

#     for m in range(num_modes):
#         if np.all(gaps_vs_sigma[m] == 0):
#             continue
#         plt.plot(
#             sigmas,
#             gaps_vs_sigma[m],
#             marker="o",
#             label=f"{m+2}-{m+3}"
#         )

#     plt.xscale("log")
#     plt.xlabel("Sigma")
#     plt.ylabel("Eigen gap")
#     plt.title("Eigen gaps across sigma sweep")
#     plt.grid(True, alpha=0.3)
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(
#         os.path.join(output_dir, "eigengaps_vs_sigma.png"),
#         dpi=300
#     )
#     plt.close()

#     # ------------------------------------------------------
#     # 7. FINAL CLUSTERING (USING STRONGEST MODE)
#     # ------------------------------------------------------

#     best_mode = sigma_df["best_sigma"].idxmax()
#     best_k = int(best_mode.split("-")[0])
#     best_sigma = sigma_df.loc[best_mode, "best_sigma"]

#     print(f"Selected k={best_k}, sigma={best_sigma:.4f}")

#     A = np.exp(-sq_dist / (2 * best_sigma**2))
#     np.fill_diagonal(A, 0)

#     D = np.sum(A, axis=1)
#     D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#     L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

#     eigvals, eigvecs = np.linalg.eigh(L_sym)
#     idx = np.argsort(eigvals)

#     U = eigvecs[:, idx[:best_k]]
#     U = U / np.linalg.norm(U, axis=1, keepdims=True)

#     labels = KMeans(
#         n_clusters=best_k,
#         random_state=42,
#         n_init="auto"
#     ).fit_predict(U)

#     clustered = pd.DataFrame({
#         "month": month_labels,
#         "cluster": labels
#     })

#     clustered.to_csv(
#         os.path.join(output_dir, "monthly_clusters.csv"),
#         index=False
#     )

#     # ------------------------------------------------------
#     # 8. SAVE FEATURE MATRICES PER CLUSTER
#     # ------------------------------------------------------

#     for cluster in np.unique(labels):
#         idxs = np.where(labels == cluster)[0]
#         cluster_matrix = X[idxs, :]

#         np.savetxt(
#             os.path.join(output_dir, f"cluster_{cluster}_features.csv"),
#             cluster_matrix,
#             delimiter=","
#         )

#         print(
#             f"Cluster {cluster}: feature matrix shape "
#             f"{cluster_matrix.shape}"
#         )

#     # ------------------------------------------------------
#     # 9. CLUSTER AVERAGE PROFILES
#     # ------------------------------------------------------

#     df_hourly["month_str"] = (
#         df_hourly["year"].astype(str) + "-" +
#         df_hourly["month"].astype(str).str.zfill(2)
#     )

#     merged = df_hourly.merge(
#         clustered, left_on="month_str", right_on="month"
#     )

#     for c in range(best_k):

#         cd = merged[merged["cluster"] == c]
#         if cd.empty:
#             continue

#         avg_step = cd.groupby("hour")["step_length"].mean()
#         avg_turn = cd.groupby("hour")["turning_angle"].mean()

#         plt.figure(figsize=(12, 5))

#         plt.subplot(1, 2, 1)
#         plt.plot(avg_step.index, avg_step.values, marker="o")
#         plt.title(f"Cluster {c} – Step length")
#         plt.grid(True)

#         plt.subplot(1, 2, 2)
#         plt.plot(avg_turn.index, avg_turn.values, marker="o")
#         plt.title(f"Cluster {c} – Turning angle")
#         plt.grid(True)

#         plt.tight_layout()
#         plt.savefig(
#             os.path.join(output_dir, f"cluster_{c}_profiles.png"),
#             dpi=300
#         )
#         plt.close()


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
#         run_spectral_pipeline(csv_path, output_dir)


'''Select the Sigma '''


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ==========================================================
# PATH SETUP
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "segments")
RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

os.environ["OMP_NUM_THREADS"] = "1"

eps = 1e-8
MAX_K = 10

# ==========================================================
# CORE PIPELINE
# ==========================================================

def run_spectral_pipeline(csv_path, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------
    # 1. LOAD DATA
    # ------------------------------------------------------

    df = pd.read_csv(csv_path)
    df["datetime"] = pd.to_datetime(df["datetime"])

    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["hour"] = df["datetime"].dt.hour

    df_hourly = (
        df.groupby(["year", "month", "hour"])
          .agg({
              "step_length": "sum",
              "turning_angle": "mean"
          })
          .reset_index()
    )

    # ------------------------------------------------------
    # 2. BUILD 48-D FEATURE MATRIX
    # ------------------------------------------------------

    features = []
    month_labels = []

    for (year, month), g in df_hourly.groupby(["year", "month"]):
        g = g.sort_values("hour")

        if len(g) != 24:
            continue

        x_i = np.hstack([
            g["step_length"].values,
            g["turning_angle"].values
        ])

        features.append(x_i)
        month_labels.append(f"{year}-{month:02d}")

    X = np.array(features)

    if X.shape[0] < 3:
        print(f"Skipping {os.path.basename(csv_path)} (too few months)")
        return

    # Save the feature matrix used for spectral clustering as a CSV
    feature_df = pd.DataFrame(X)
    feature_df.index = month_labels
    feature_df.to_csv(
        os.path.join(output_dir, "feature_matrix_for_clustering.csv")
    )

    # ------------------------------------------------------
    # 3. STANDARDIZATION
    # ------------------------------------------------------

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    n = X_scaled.shape[0]

    sq_dist = np.sum(
        (X_scaled[:, None, :] - X_scaled[None, :, :]) ** 2,
        axis=-1
    )

    # ------------------------------------------------------
    # 4. SIGMA SWEEP + EIGENGAPS
    # ------------------------------------------------------

    sigmas = np.logspace(-1, 1.5, 30)
    num_modes = MAX_K - 1
    gaps_vs_sigma = np.zeros((num_modes, len(sigmas)))

    for s, sigma in enumerate(sigmas):

        A = np.exp(-sq_dist / (2 * sigma**2))
        np.fill_diagonal(A, 0)

        D = np.sum(A, axis=1)
        if np.any(D < eps):
            continue

        D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
        L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

        eigvals = np.sort(np.linalg.eigvalsh(L_sym))
        gaps = np.diff(eigvals)

        for m in range(min(num_modes, len(gaps) - 1)):
            gaps_vs_sigma[m, s] = gaps[m + 1]

    # ------------------------------------------------------
    # 5. SAVE SIGMA VALUES PER MODE
    # ------------------------------------------------------

    sigma_modes = {}

    for m in range(num_modes):
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
    # 6. EIGENGAP PLOT
    # ------------------------------------------------------

    plt.figure(figsize=(9, 5))

    for m in range(num_modes):
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
        # 7. FINAL CLUSTERING (USING SELECTED MODE)
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
            "month": month_labels,
            "cluster": labels
        })
        clustered.to_csv(
            os.path.join(output_dir, f"monthly_clusters_{selected_mode}.csv"),
            index=False
        )
        # ------------------------------------------------------
        # 8. SAVE FEATURE MATRICES PER CLUSTER
        # ------------------------------------------------------
        for cluster in np.unique(labels):
            idxs = np.where(labels == cluster)[0]
            cluster_matrix = X[idxs, :]
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
        # 9. CLUSTER AVERAGE PROFILES
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
            avg_step = cd.groupby("hour")["step_length"].mean()
            avg_turn = cd.groupby("hour")["turning_angle"].mean()
            plt.figure(figsize=(12, 5))
            plt.subplot(1, 2, 1)
            plt.plot(avg_step.index, avg_step.values, marker="o")
            plt.title(f"Cluster {c} – Step length")
            plt.grid(True)
            plt.subplot(1, 2, 2)
            plt.plot(avg_turn.index, avg_turn.values, marker="o")
            plt.title(f"Cluster {c} – Turning angle")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, f"cluster_{c}_profiles_{selected_mode}.png"),
                dpi=300
            )
            plt.close()


# ==========================================================
# BATCH PROCESS
# ==========================================================

for group in ["fe", "me"]:

    group_dir = os.path.join(SEGMENTS_DIR, group)
    result_group_dir = os.path.join(RESULTS_DIR, group)
    os.makedirs(result_group_dir, exist_ok=True)

    for file in sorted(os.listdir(group_dir)):

        if not file.endswith(".csv"):
            continue

        file_id = file.split("_")[0]
        csv_path = os.path.join(group_dir, file)
        output_dir = os.path.join(result_group_dir, file_id)

        print(f"\nProcessing: {csv_path}")
        run_spectral_pipeline(csv_path, output_dir)

'''
Consider daily parameters of step length, speed, area as a convex hull

'''

# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans
# from scipy.spatial import ConvexHull

# # ==========================================================
# # PATH SETUP
# # ==========================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "segments")
# RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")
# os.makedirs(RESULTS_DIR, exist_ok=True)
# os.environ["OMP_NUM_THREADS"] = "1"
# eps = 1e-8
# MAX_K = 10

# # ==========================================================
# # CORE PIPELINE
# # ==========================================================
# def run_spectral_pipeline(csv_path, output_dir):
#     os.makedirs(output_dir, exist_ok=True)
#     # ------------------------------------------------------
#     # 1. LOAD DATA
#     # ------------------------------------------------------
#     df = pd.read_csv(csv_path)
#     df["datetime"] = pd.to_datetime(df["datetime"])
#     df["date"] = df["datetime"].dt.date
#     # ------------------------------------------------------
#     # 2. BUILD DAILY FEATURE MATRIX
#     # ------------------------------------------------------
#     features = []
#     date_labels = []
#     for date, g in df.groupby("date"):
#         if len(g) < 3:  # Need at least 3 points for hull
#             continue
#         total_step = g["step_length"].sum()
#         mean_speed = g["speed"].mean()
#         std_turn = g["turning_angle"].std()
#         points = g[["Longitude", "Latitude"]].values
#         try:
#             hull = ConvexHull(points)
#             area = hull.area  # Approx sq deg
#         except:
#             area = 0.0
#         x_i = np.array([total_step, mean_speed, std_turn, area])
#         features.append(x_i)
#         date_labels.append(str(date))
#     X = np.array(features)
#     if X.shape[0] < 3:
#         print(f"Skipping {os.path.basename(csv_path)} (too few days)")
#         return
#     # ------------------------------------------------------
#     # 3. STANDARDIZATION
#     # ------------------------------------------------------
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)
#     n = X_scaled.shape[0]
#     sq_dist = np.sum(
#         (X_scaled[:, None, :] - X_scaled[None, :, :]) ** 2,
#         axis=-1
#     )
#     # ------------------------------------------------------
#     # 4. SIGMA SWEEP + EIGENGAPS
#     # ------------------------------------------------------
#     sigmas = np.logspace(-1, 1.5, 30)
#     num_modes = MAX_K - 1
#     gaps_vs_sigma = np.zeros((num_modes, len(sigmas)))
#     for s, sigma in enumerate(sigmas):
#         A = np.exp(-sq_dist / (2 * sigma**2))
#         np.fill_diagonal(A, 0)
#         D = np.sum(A, axis=1)
#         if np.any(D < eps):
#             continue
#         D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#         L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt
#         eigvals = np.sort(np.linalg.eigvalsh(L_sym))
#         gaps = np.diff(eigvals)
#         for m in range(min(num_modes, len(gaps) - 1)):
#             gaps_vs_sigma[m, s] = gaps[m + 1]
#     # ------------------------------------------------------
#     # 5. SAVE SIGMA VALUES PER MODE
#     # ------------------------------------------------------
#     sigma_modes = {}
#     for m in range(num_modes):
#         if np.all(gaps_vs_sigma[m] == 0):
#             continue
#         best_sigma_idx = np.argmax(gaps_vs_sigma[m])
#         sigma_modes[f"{m+2}-{m+3}"] = sigmas[best_sigma_idx]
#     sigma_df = pd.DataFrame.from_dict(
#         sigma_modes, orient="index", columns=["best_sigma"]
#     )
#     sigma_df.index.name = "eigengap_mode"
#     sigma_df.to_csv(
#         os.path.join(output_dir, "sigma_per_eigengap_mode.csv")
#     )
#     # ------------------------------------------------------
#     # 6. EIGENGAP PLOT
#     # ------------------------------------------------------
#     plt.figure(figsize=(9, 5))
#     for m in range(num_modes):
#         if np.all(gaps_vs_sigma[m] == 0):
#             continue
#         plt.plot(
#             sigmas,
#             gaps_vs_sigma[m],
#             marker="o",
#             label=f"{m+2}-{m+3}"
#         )
#     plt.xscale("log")
#     plt.xlabel("Sigma")
#     plt.ylabel("Eigen gap")
#     plt.title("Eigen gaps across sigma sweep")
#     plt.grid(True, alpha=0.3)
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(
#         os.path.join(output_dir, "eigengaps_vs_sigma.png"),
#         dpi=300
#     )
    


#     plt.show()
#     # Ask for the eigengap mode
#     print("Available eigengap modes:", list(sigma_modes.keys()))
#     selected_mode = input("Enter the eigengap mode (e.g., 2-3): ").strip()
#     if selected_mode not in sigma_modes:
#         print(f"Invalid mode: {selected_mode}. Available: {list(sigma_modes.keys())}")
#         return
#     else:
#         best_k = int(selected_mode.split("-")[0])
#         best_sigma = sigma_modes[selected_mode]
#         print(f"Selected mode: {selected_mode}, k={best_k}, sigma={best_sigma:.4f}")
#         # ------------------------------------------------------
#         # 7. FINAL CLUSTERING (USING SELECTED MODE)
#         # ------------------------------------------------------
#         A = np.exp(-sq_dist / (2 * best_sigma**2))
#         np.fill_diagonal(A, 0)
#         D = np.sum(A, axis=1)
#         D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#         L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt
#         eigvals, eigvecs = np.linalg.eigh(L_sym)
#         idx = np.argsort(eigvals)