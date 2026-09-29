'''Features: Temperature and precipitation '''

# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans

# # ==========================================================
# # CORE PIPELINE
# # ==========================================================

# def run_spectral_pipeline(csv_path, output_dir):

#     os.makedirs(output_dir, exist_ok=True)

#     # ------------------------------------------------------
#     # 1. LOAD DATA
#     # ------------------------------------------------------

#     df = pd.read_csv(csv_path)
#     df["date"] = pd.to_datetime(df["date"])

#     df["year"] = df["date"].dt.year
#     df["month"] = df["date"].dt.month
#     df["day"] = df["date"].dt.day

#     # ------------------------------------------------------
#     # 2. BUILD 62-D FEATURE MATRIX (31 days Temp + 31 days Precip, padded)
#     # ------------------------------------------------------

#     features = []
#     month_labels = []

#     for (year, month), g in df.groupby(["year", "month"]):
#         g = g.sort_values("day")

#         days_present = len(g)
#         if days_present < 28:
#             continue  # Skip incomplete months (unlikely)

#         mean_temp = g["Temp_C"].mean()

#         temp = g["Temp_C"].values
#         precip = g["Precip_mm"].values

#         pad_len = 31 - days_present
#         temp_padded = np.concatenate((temp, np.full(pad_len, mean_temp)))
#         precip_padded = np.concatenate((precip, np.zeros(pad_len)))

#         x_i = np.hstack((temp_padded, precip_padded))

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

#     eps = 1e-8
#     MAX_K = 10

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
#     best_k = int(best_mode.split("-")[1])
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

#     df["month_str"] = (
#         df["year"].astype(str) + "-" +
#         df["month"].astype(str).str.zfill(2)
#     )

#     merged = df.merge(
#         clustered, left_on="month_str", right_on="month"
#     )

#     for c in range(best_k):

#         cd = merged[merged["cluster"] == c]
#         if cd.empty:
#             continue

#         avg_temp = cd.groupby("day")["Temp_C"].mean()
#         avg_precip = cd.groupby("day")["Precip_mm"].mean()

#         plt.figure(figsize=(12, 5))

#         plt.subplot(1, 2, 1)
#         plt.plot(avg_temp.index, avg_temp.values, marker="o")
#         plt.title(f"Cluster {c} – Temp_C")
#         plt.grid(True)

#         plt.subplot(1, 2, 2)
#         plt.plot(avg_precip.index, avg_precip.values, marker="o")
#         plt.title(f"Cluster {c} – Precip_mm")
#         plt.grid(True)

#         plt.tight_layout()
#         plt.savefig(
#             os.path.join(output_dir, f"cluster_{c}_profiles.png"),
#             dpi=300
#         )
#         plt.close()

# os.environ["OMP_NUM_THREADS"] = "1"

# if __name__ == "__main__":
#     csv_path = "okaukuejo_daily_2010_2013.csv"
#     output_dir = "results"
#     run_spectral_pipeline(csv_path, output_dir)



'''with values for precipitation only '''


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
os.environ["OMP_NUM_THREADS"] = "1"
eps = 1e-8
MAX_K = 10
csv_path = "okaukuejo_daily_2010_2013.csv"
output_dir = "results/Humidity"
os.makedirs(output_dir, exist_ok=True)
# ------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------
df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"], format='%m/%d/%Y')
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
# ------------------------------------------------------
# 2. BUILD 31-D FEATURE MATRIX (31 days Precip_mm, padded)
# ------------------------------------------------------
features = []
month_labels = []
for (year, month), g in df.groupby(["year", "month"]):
    g = g.sort_values("day")
    days_present = len(g)
    if days_present < 28:
        continue  # Skip incomplete months (unlikely)
    precip = g["Humidity"].values
    pad_len = 31 - days_present
    precip_padded = np.concatenate((precip, np.zeros(pad_len)))
    features.append(precip_padded)
    month_labels.append(f"{year}-{month:02d}")
X = np.array(features)
if X.shape[0] < 3:
    print(f"Skipping {os.path.basename(csv_path)} (too few months)")
else:
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
        os.path.join(output_dir, "sigma_per_eigengap_mode.csv")
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
        os.path.join(output_dir, "eigengaps_vs_sigma.png"),
        dpi=300
    )
    # Show the plot interactively
    plt.show()
    # Ask for the eigengap mode
    print("Available eigengap modes:", list(sigma_modes.keys()))
    selected_mode = input("Enter the eigengap mode (e.g., 2-3): ").strip()
    if selected_mode not in sigma_modes:
        print(f"Invalid mode: {selected_mode}. Available: {list(sigma_modes.keys())}")
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
        df["month_str"] = (
            df["year"].astype(str) + "-" +
            df["month"].astype(str).str.zfill(2)
        )
        merged = df.merge(
            clustered, left_on="month_str", right_on="month"
        )
        for c in range(best_k):
            cd = merged[merged["cluster"] == c]
            if cd.empty:
                continue
            avg_precip = cd.groupby("day")["Humidity"].mean()
            plt.figure(figsize=(6, 5))
            plt.plot(avg_precip.index, avg_precip.values, marker="o")
            plt.title(f"Cluster {c} – Humidity")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, f"cluster_{c}_profiles_{selected_mode}.png"),
                dpi=300
            )
            plt.close()