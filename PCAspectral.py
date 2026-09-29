# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.cluster import KMeans

# # ==========================================================
# # 1. PATH SETUP
# # ==========================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # Input: Path where your PCA results are stored
# INPUT_DIR = os.path.join(BASE_DIR, "..", "results", "PCAVector", "fe", "03fe")
# # Output: New directory for Clustering results
# OUTPUT_DIR = os.path.join(BASE_DIR, "..", "results", "PCASpectral", "fe", "03fe")
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # File names
# PCA_FILE = "pca_projected_features_90.csv"
# ORIGINAL_FEATURES_FILE = "feature_matrix_for_clustering.csv"

# # ==========================================================
# # 2. LOAD DATA
# # ==========================================================
# # Load PCA reduced features (The coordinates for clustering)
# pca_path = os.path.join(INPUT_DIR, PCA_FILE)
# if not os.path.exists(pca_path):
#     raise FileNotFoundError(f"Missing PCA file: {pca_path}. Run PCA script first.")

# df_pca = pd.read_csv(pca_path, index_col=0)
# # Use PCA scores directly without re-standardizing to preserve variance weighting
# X_input = df_pca.values 
# month_labels = df_pca.index.tolist()

# # Load original feature matrix for final cluster saving
# original_data_path = os.path.join(BASE_DIR, "..", "results", "120D", "fe", "03fe", ORIGINAL_FEATURES_FILE)
# df_original = pd.read_csv(original_data_path, index_col=0)

# # ==========================================================
# # 3. DISTANCE CALCULATION
# # ==========================================================
# n = X_input.shape[0]
# eps = 1e-10
# MAX_K = 10

# # Compute squared Euclidean distance matrix in the PCA space 
# # Note: PC1 will naturally have more "weight" here because its values have higher variance
# sq_dist = np.sum(
#     (X_input[:, None, :] - X_input[None, :, :]) ** 2,
#     axis=-1
# )

# # ==========================================================
# # 4. SIGMA SWEEP + EIGENGAPS
# # ==========================================================
# sigmas = np.logspace(-1, 1.5, 30)
# num_modes = MAX_K - 1
# gaps_vs_sigma = np.zeros((num_modes, len(sigmas)))

# for s, sigma in enumerate(sigmas):
#     # Gaussian Affinity Matrix
#     A = np.exp(-sq_dist / (2 * sigma**2))
#     np.fill_diagonal(A, 0)

#     # Degree Matrix and Laplacian
#     D = np.sum(A, axis=1)
#     if np.any(D < eps):
#         continue

#     D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#     L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

#     # Eigenvalues for the gap calculation
#     eigvals = np.sort(np.linalg.eigvalsh(L_sym))
#     gaps = np.diff(eigvals)

#     for m in range(min(num_modes, len(gaps) - 1)):
#         gaps_vs_sigma[m, s] = gaps[m + 1]

# # ==========================================================
# # 5. SAVE SIGMA VALUES PER MODE
# # ==========================================================
# sigma_modes = {}
# for m in range(num_modes):
#     if np.all(gaps_vs_sigma[m] == 0):
#         continue
#     best_sigma_idx = np.argmax(gaps_vs_sigma[m])
#     sigma_modes[f"{m+2}-{m+3}"] = sigmas[best_sigma_idx]

# sigma_df = pd.DataFrame.from_dict(
#     sigma_modes, orient="index", columns=["best_sigma"]
# )
# sigma_df.index.name = "eigengap_mode"
# sigma_df.to_csv(os.path.join(OUTPUT_DIR, "sigma_per_eigengap_mode_Hourly.csv"))

# # ==========================================================
# # 6. EIGENGAP PLOT
# # ==========================================================
# plt.figure(figsize=(9, 5))
# for m in range(num_modes):
#     if np.all(gaps_vs_sigma[m] == 0):
#         continue
#     plt.plot(sigmas, gaps_vs_sigma[m], marker="o", label=f"{m+2}-{m+3}")

# plt.xscale("log")
# plt.xlabel("Sigma")
# plt.ylabel("Eigen gap")
# plt.title("Eigen gaps across sigma sweep (PCA Input - Variance Preserved)")
# plt.grid(True, alpha=0.3)
# plt.legend()
# plt.tight_layout()
# plt.savefig(os.path.join(OUTPUT_DIR, "eigengaps_vs_sigma_Hourly.png"), dpi=300)
# plt.show()

# # ==========================================================
# # 7. FINAL CLUSTERING
# # ==========================================================
# print("Available eigengap modes:", list(sigma_modes.keys()))
# selected_mode = input("Enter the eigengap mode (e.g., 2-3): ").strip()

# if selected_mode not in sigma_modes:
#     print(f"Invalid mode: {selected_mode}. Available: {list(sigma_modes.keys())}")
# else:
#     best_k = int(selected_mode.split("-")[0])
#     best_sigma = sigma_modes[selected_mode]
#     print(f"Clustering with mode: {selected_mode}, k={best_k}, sigma={best_sigma:.4f}")

#     # Build final Affinity and Laplacian
#     A = np.exp(-sq_dist / (2 * best_sigma**2))
#     np.fill_diagonal(A, 0)
#     D = np.sum(A, axis=1)
#     D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
#     L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

#     # Eigen-projection
#     eigvals, eigvecs = np.linalg.eigh(L_sym)
#     idx = np.argsort(eigvals)
#     U = eigvecs[:, idx[:best_k]]
#     # Normalizing rows to the unit circle (Standard practice for L_sym)
#     U = U / np.linalg.norm(U, axis=1, keepdims=True)

#     # K-Means in spectral space
#     labels = KMeans(n_clusters=best_k, random_state=42, n_init="auto").fit_predict(U)

#     clustered = pd.DataFrame({"month": month_labels, "cluster": labels})
#     clustered.to_csv(os.path.join(OUTPUT_DIR, f"monthly_clusters_{selected_mode}.csv"), index=False)

#     # ==========================================================
#     # 8. SAVE FEATURE MATRICES PER CLUSTER
#     # ==========================================================
#     for cluster in np.unique(labels):
#         idxs = np.where(labels == cluster)[0]
#         cluster_matrix = df_original.iloc[idxs, :].values
#         np.savetxt(
#             os.path.join(OUTPUT_DIR, f"cluster_{cluster}_features_{selected_mode}.csv"),
#             cluster_matrix,
#             delimiter=","
#         )
#         print(f"Cluster {cluster}: feature matrix shape {cluster_matrix.shape}")

# print("\n--- Spectral Clustering Analysis Complete ---")






import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# ==========================================================
# 1. PATH SETUP - BATCH PROCESSING
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base directories
PCA_BASE_DIR = os.path.join(BASE_DIR, "..", "results", "PCAVector", "me")
SPECTRAL_BASE_DIR = os.path.join(BASE_DIR, "..", "results", "PCASpectral", "me")
ORIGINAL_BASE_DIR = os.path.join(BASE_DIR, "..", "results", "120D", "me")

os.makedirs(SPECTRAL_BASE_DIR, exist_ok=True)

# Get all subfolders (01fe, 02fe, ..., 08fe)
subfolders = sorted([m for m in os.listdir(PCA_BASE_DIR) 
                    if os.path.isdir(os.path.join(PCA_BASE_DIR, m)) and m.endswith('me')])

print(f"Found {len(subfolders)} elephant folders to process: {subfolders}")

# ==========================================================
# MAIN LOOP OVER ALL ELEPHANTS
# ==========================================================
for folder in subfolders:
    print(f"\n{'='*70}")
    print(f"Processing Spectral Clustering for Elephant Folder: {folder}")
    print(f"{'='*70}")
    
    # Set paths for current folder
    INPUT_DIR = os.path.join(PCA_BASE_DIR, folder)
    OUTPUT_DIR = os.path.join(SPECTRAL_BASE_DIR, folder)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # File names (adjusted for batch)
    PCA_FILE = f"pca_projected_features_90_{folder}.csv"
    ORIGINAL_FEATURES_FILE = "feature_matrix_for_clustering.csv"
    
    # ==========================================================
    # 2. LOAD DATA
    # ==========================================================
    pca_path = os.path.join(INPUT_DIR, PCA_FILE)
    if not os.path.exists(pca_path):
        print(f"Warning: PCA file not found for {folder}: {pca_path}")
        print("Skipping this folder...")
        continue
    
    df_pca = pd.read_csv(pca_path, index_col=0)
    X_input = df_pca.values
    month_labels = df_pca.index.tolist()
    
    # Load original feature matrix
    original_data_path = os.path.join(ORIGINAL_BASE_DIR, folder, ORIGINAL_FEATURES_FILE)
    if not os.path.exists(original_data_path):
        original_data_path = os.path.join(ORIGINAL_BASE_DIR, folder, "feature_matrix_120D.csv")
    
    if os.path.exists(original_data_path):
        df_original = pd.read_csv(original_data_path, index_col=0)
    else:
        print(f"Warning: Original features file not found for {folder}")
        df_original = None
    
    # ==========================================================
    # 3. DISTANCE CALCULATION
    # ==========================================================
    n = X_input.shape[0]
    eps = 1e-10
    MAX_K = 10
    sq_dist = np.sum(
        (X_input[:, None, :] - X_input[None, :, :]) ** 2,
        axis=-1
    )
    
    # ==========================================================
    # 4. SIGMA SWEEP + EIGENGAPS
    # ==========================================================
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
    
    # ==========================================================
    # 5. SAVE SIGMA VALUES PER MODE
    # ==========================================================
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
    sigma_df.to_csv(os.path.join(OUTPUT_DIR, f"sigma_per_eigengap_mode_Hourly_{folder}.csv"))
    
    # ==========================================================
    # 6. EIGENGAP PLOT
    # ==========================================================
    plt.figure(figsize=(9, 5))
    for m in range(num_modes):
        if np.all(gaps_vs_sigma[m] == 0):
            continue
        plt.plot(sigmas, gaps_vs_sigma[m], marker="o", label=f"{m+2}-{m+3}")
    
    plt.xscale("log")
    plt.xlabel("Sigma")
    plt.ylabel("Eigen gap")
    plt.title(f"Eigen gaps across sigma sweep (PCA Input) - {folder}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"eigengaps_vs_sigma_Hourly_{folder}.png"), dpi=300)
    plt.show()
    
    # ==========================================================
    # 7. FINAL CLUSTERING - INTERACTIVE MODE SELECTION (as requested)
    # ==========================================================
    print(f"\nAvailable eigengap modes for {folder}:", list(sigma_modes.keys()))
    selected_mode = input(f"Enter the eigengap mode for {folder} (e.g., 2-3): ").strip()
    
    if selected_mode not in sigma_modes:
        print(f"Invalid mode: {selected_mode}. Available: {list(sigma_modes.keys())}")
        print("Skipping clustering for this folder.")
        continue
    else:
        best_k = int(selected_mode.split("-")[0])
        best_sigma = sigma_modes[selected_mode]
        print(f"Clustering with mode: {selected_mode}, k={best_k}, sigma={best_sigma:.4f}")
        
        # Build final Affinity and Laplacian
        A = np.exp(-sq_dist / (2 * best_sigma**2))
        np.fill_diagonal(A, 0)
        D = np.sum(A, axis=1)
        D_inv_sqrt = np.diag(1.0 / np.sqrt(D + eps))
        L_sym = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt
        
        # Eigen-projection
        eigvals, eigvecs = np.linalg.eigh(L_sym)
        idx = np.argsort(eigvals)
        U = eigvecs[:, idx[:best_k]]
        U = U / np.linalg.norm(U, axis=1, keepdims=True)
        
        # K-Means in spectral space
        labels = KMeans(n_clusters=best_k, random_state=42, n_init="auto").fit_predict(U)
        
        clustered = pd.DataFrame({"month": month_labels, "cluster": labels})
        clustered.to_csv(os.path.join(OUTPUT_DIR, f"monthly_clusters_{selected_mode}_{folder}.csv"), index=False)
        
        # ==========================================================
        # 8. SAVE FEATURE MATRICES PER CLUSTER
        # ==========================================================
        if df_original is not None:
            for cluster in np.unique(labels):
                idxs = np.where(labels == cluster)[0]
                cluster_matrix = df_original.iloc[idxs, :].values
                np.savetxt(
                    os.path.join(OUTPUT_DIR, f"cluster_{cluster}_features_{selected_mode}_{folder}.csv"),
                    cluster_matrix,
                    delimiter=","
                )
                print(f"Cluster {cluster}: feature matrix shape {cluster_matrix.shape}")
        
    print(f"--- Spectral Clustering Complete for {folder} ---\n")

print("\n All folders processed successfully!")