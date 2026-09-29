# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.preprocessing import StandardScaler

# # ==========================================================
# # PATH SETUP
# # ==========================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # Location of your 120D feature matrix
# DATA_DIR = os.path.join(BASE_DIR, "..", "results", "120D", "fe", "01fe")
# # Location to save PCA plots and reports
# RESULTS_DIR = os.path.join(BASE_DIR, "..", "results", "PCA")

# os.makedirs(RESULTS_DIR, exist_ok=True)

# # ==========================================================
# # 1. LOAD DATA
# # ==========================================================
# csv_path = os.path.join(DATA_DIR, "feature_matrix_120D.csv")
# if not os.path.exists(csv_path):
#     # Fallback to your other naming convention if necessary
#     csv_path = os.path.join(DATA_DIR, "feature_matrix_for_clustering.csv")

# print(f"Loading data from: {csv_path}")
# df_features = pd.read_csv(csv_path, index_col=0)
# X = df_features.values

# # Standardize: Critical for mixed units (meters/degrees/NSD)
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)

# # ==========================================================
# # 2. PCA CLASS
# # ==========================================================
# class MovementPCA:
#     def __init__(self, n_components):
#         self.n_components = n_components
#         self.components = None
#         self.eigenvalues = None
#         self.explained_variance = None
#         self.cov_matrix = None

#     def fit(self, X):
#         X_centered = X - np.mean(X, axis=0)
        
#         # Covariance Matrix
#         self.cov_matrix = np.cov(X_centered, rowvar=False)
        
#         # Eigen Analysis
#         eigenvalues, eigenvectors = np.linalg.eig(self.cov_matrix)
        
#         # Convert to real numbers (handling small imaginary parts from float precision)
#         eigenvalues = np.real(eigenvalues)
#         eigenvectors = np.real(eigenvectors)
        
#         # Sort indices
#         idx = np.argsort(eigenvalues)[::-1]
#         self.eigenvalues = eigenvalues[idx]
#         self.components = eigenvectors[:, idx][:, :self.n_components]
        
#         # Variance
#         total_var = np.sum(self.eigenvalues)
#         self.explained_variance = self.eigenvalues[:self.n_components] / total_var

# # Fit model for all features
# pca_mov = MovementPCA(n_components=X.shape[1])
# pca_mov.fit(X_scaled)

# # ==========================================================
# # 3. GENERATE AND SAVE PLOTS
# # ==========================================================

# # A. COVARIANCE HEATMAP
# # Helps visualize which hour blocks or metrics are redundant
# plt.figure(figsize=(12, 10))
# sns.heatmap(pca_mov.cov_matrix, cmap='coolwarm', center=0, xticklabels=False, yticklabels=False)
# plt.title("Covariance Matrix: Redundancy in 120 Movement Features")
# plt.savefig(os.path.join(RESULTS_DIR, "01_covariance_heatmap.png"), dpi=300)
# plt.show()

# # B. ELBOW METHOD (SCREE PLOT)
# # Determines how many principal components actually matter

# cum_var = np.cumsum(pca_mov.explained_variance)
# plt.figure(figsize=(10, 6))
# n_show = min(15, len(pca_mov.explained_variance)) # Show first 15 components
# plt.bar(range(1, n_show + 1), pca_mov.explained_variance[:n_show], alpha=0.6, label="Individual Variance")
# plt.step(range(1, n_show + 1), cum_var[:n_show], where='mid', label="Cumulative Variance", color='red')
# plt.axhline(y=0.90, color='black', linestyle='--', label="90% Threshold")
# plt.xlabel("Principal Components")
# plt.ylabel("Explained Variance Ratio")
# plt.title("Scree Plot: How many dimensions are needed?")
# plt.legend()
# plt.grid(alpha=0.3)
# plt.savefig(os.path.join(RESULTS_DIR, "02_scree_plot_elbow.png"), dpi=300)
# plt.show()

# # ==========================================================
# # 4. FEATURE INFLUENCE (LOADINGS)
# # ==========================================================
# # Loadings = Eigenvectors * sqrt(Eigenvalues)
# # Focus on PC1: the axis of maximum behavioral difference
# loadings = pca_mov.components[:, 0] * np.sqrt(pca_mov.eigenvalues[0])
# loadings_df = pd.Series(loadings, index=df_features.columns).abs().sort_values(ascending=False)

# # Save the full importance list to CSV for your paper's appendix
# loadings_df.to_csv(os.path.join(RESULTS_DIR, "feature_importance_loadings.csv"))

# # C. TOP 20 INFLUENTIAL FEATURES BAR CHART
# plt.figure(figsize=(12, 8))
# loadings_df.head(20).plot(kind='bar', color='midnightblue')
# plt.title("Top 20 Most Influential Features (PC1 Loadings)")
# plt.ylabel("Absolute Loading Score (Importance)")
# plt.xlabel("Feature Name (Metric + Hour)")
# plt.xticks(rotation=45, ha='right')
# plt.tight_layout()
# plt.savefig(os.path.join(RESULTS_DIR, "03_feature_importance.png"), dpi=300)
# plt.show()

# print("\n--- Feature Selection Analysis Complete ---")
# print(f"Plots and CSV saved to: {RESULTS_DIR}")
# print("\nTop 5 Most Influential Movement Features:")
# print(loadings_df.head(5))

# '''
# Dimension Reduction

# '''

# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.preprocessing import StandardScaler

# # ==========================================================
# # PATH SETUP
# # ==========================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(BASE_DIR, "..", "results", "120D", "fe", "03fe")
# RESULTS_DIR = os.path.join(BASE_DIR, "..", "results", "PCAVector", "fe", "03fe")
# os.makedirs(RESULTS_DIR, exist_ok=True)

# # 1. LOAD DATA
# csv_path = os.path.join(DATA_DIR, "feature_matrix_120D.csv")
# if not os.path.exists(csv_path):
#     csv_path = os.path.join(DATA_DIR, "feature_matrix_for_clustering.csv")

# df_features = pd.read_csv(csv_path, index_col=0)
# X = df_features.values

# # Standardize
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)

# # 2. PCA IMPLEMENTATION
# X_centered = X_scaled - np.mean(X_scaled, axis=0)
# cov_matrix = np.cov(X_centered, rowvar=False)
# eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

# eigenvalues = np.real(eigenvalues)
# eigenvectors = np.real(eigenvectors)

# idx = np.argsort(eigenvalues)[::-1]
# eigenvalues = eigenvalues[idx]
# eigenvectors = eigenvectors[:, idx]

# total_var = np.sum(eigenvalues)
# explained_variance = eigenvalues / total_var
# cum_var = np.cumsum(explained_variance)

# # Updated to 90%
# n_components_90 = np.argmax(cum_var >= 0.90) + 1

# # 3. FEATURE REDUCTION & LOADINGS
# selected_eigenvectors = eigenvectors[:, :n_components_90]
# loadings = selected_eigenvectors * np.sqrt(eigenvalues[:n_components_90])

# loadings_df = pd.DataFrame(
#     loadings,
#     index=df_features.columns,
#     columns=[f"PC{i+1}" for i in range(n_components_90)]
# )

# X_pca_projected = X_scaled @ selected_eigenvectors
# pca_projected_df = pd.DataFrame(
#     X_pca_projected,
#     index=df_features.index,
#     columns=[f"PC{i+1}" for i in range(n_components_90)]
# )

# # Save results
# loadings_df.to_csv(os.path.join(RESULTS_DIR, "pca_loadings_90.csv"))
# pca_projected_df.to_csv(os.path.join(RESULTS_DIR, "pca_projected_features_90.csv"))

# # ==========================================================
# # 4. INTERPRETATION VISUALIZATION (Heatmap)
# # ==========================================================
# def plot_pc_heatmap(pc_name, save_name):
#     # Split feature names into Metric and Hour (Assumes format Metric_Hour)
#     temp_df = loadings_df[[pc_name]].copy()
#     temp_df['metric'] = [f.rsplit('_', 1)[0] for f in temp_df.index]
#     temp_df['hour'] = [int(f.rsplit('_', 1)[1]) for f in temp_df.index]
    
#     # Pivot for Heatmap
#     heatmap_data = temp_df.pivot(index="metric", columns="hour", values=pc_name)
    
#     plt.figure(figsize=(15, 7))
#     sns.heatmap(heatmap_data, cmap="RdBu_r", center=0, annot=False, 
#                 cbar_kws={'label': 'Loading (Correlation)'})
#     plt.title(f"Feature Influence Map: {pc_name}")
#     plt.xlabel("Hour of Day (0-23)")
#     plt.ylabel("Movement Metric")
#     plt.tight_layout()
#     plt.savefig(os.path.join(RESULTS_DIR, save_name), dpi=300)
#     plt.show()

# # Visualize the first two main components (usually most interpretable)
# plot_pc_heatmap("PC1", "heatmap_PC1_interpretation.png")
# plot_pc_heatmap("PC2", "heatmap_PC2_interpretation.png")
# plot_pc_heatmap("PC3", "heatmap_PC3_interpretation.png")
# plot_pc_heatmap("PC4", "heatmap_PC4_interpretation.png")

# # Scree Plot
# plt.figure(figsize=(10, 6))
# plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.6, label="Individual")
# plt.step(range(1, len(explained_variance) + 1), cum_var, where='mid', label="Cumulative", color='red')
# plt.axhline(y=0.90, color='black', linestyle='--', label="90% Threshold")
# plt.axvline(x=n_components_90, color='green', linestyle=':', label=f'PC={n_components_90}')
# plt.title("Scree Plot: Finding Components for 90% Variance")
# plt.legend()
# plt.savefig(os.path.join(RESULTS_DIR, "scree_plot_90.png"), dpi=300)
# plt.show()



''' Dimension Reduction - PCA for All Elephants (01fe to 08fe) '''

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# ==========================================================
# PATH SETUP
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_BASE_DIR = os.path.join(BASE_DIR, "..", "results", "120D", "me")
RESULTS_BASE_DIR = os.path.join(BASE_DIR, "..", "results", "PCAVector", "me")

# Create base results directory
os.makedirs(RESULTS_BASE_DIR, exist_ok=True)

# Get all subfolders (01fe, 02fe, ..., 08fe)
subfolders = sorted([m for m in os.listdir(DATA_BASE_DIR) 
                    if os.path.isdir(os.path.join(DATA_BASE_DIR, m)) and m.endswith('me')])

print(f"Found {len(subfolders)} elephant folders to process: {subfolders}")

# ==========================================================
# MAIN LOOP
# ==========================================================
for folder in subfolders:
    print(f"\n{'='*60}")
    print(f"Processing: {folder}")
    print(f"{'='*60}")
    
    # Set paths for current elephant/folder
    DATA_DIR = os.path.join(DATA_BASE_DIR, folder)
    RESULTS_DIR = os.path.join(RESULTS_BASE_DIR, folder)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Find the feature matrix CSV (try both possible names)
    csv_candidates = [
        os.path.join(DATA_DIR, "feature_matrix_120D.csv"),
        os.path.join(DATA_DIR, "feature_matrix_for_clustering.csv")
    ]
    
    csv_path = None
    for candidate in csv_candidates:
        if os.path.exists(candidate):
            csv_path = candidate
            break
    
    if csv_path is None:
        print(f"Warning: No feature matrix found in {folder}. Skipping...")
        continue
    
    # 1. LOAD DATA
    df_features = pd.read_csv(csv_path, index_col=0)
    X = df_features.values
    print(f"Loaded data shape: {X.shape} (samples x features)")
    
    # 2. STANDARDIZE
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. PCA IMPLEMENTATION
    X_centered = X_scaled - np.mean(X_scaled, axis=0)
    cov_matrix = np.cov(X_centered, rowvar=False)
    
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    eigenvalues = np.real(eigenvalues)
    eigenvectors = np.real(eigenvectors)
    
    # Sort by eigenvalues descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    total_var = np.sum(eigenvalues)
    explained_variance = eigenvalues / total_var
    cum_var = np.cumsum(explained_variance)
    
    # Find number of components for 90% variance
    n_components_90 = np.argmax(cum_var >= 0.90) + 1
    print(f"Selected {n_components_90} components to explain >=90% variance")
    
    # Project data
    selected_eigenvectors = eigenvectors[:, :n_components_90]
    X_pca_projected = X_scaled @ selected_eigenvectors
    
    # Loadings (for interpretation)
    loadings = selected_eigenvectors * np.sqrt(eigenvalues[:n_components_90])
    loadings_df = pd.DataFrame(
        loadings,
        index=df_features.columns,
        columns=[f"PC{i+1}" for i in range(n_components_90)]
    )
    
    pca_projected_df = pd.DataFrame(
        X_pca_projected,
        index=df_features.index,
        columns=[f"PC{i+1}" for i in range(n_components_90)]
    )
    
    # Save results
    loadings_df.to_csv(os.path.join(RESULTS_DIR, f"pca_loadings_90_{folder}.csv"))
    pca_projected_df.to_csv(os.path.join(RESULTS_DIR, f"pca_projected_features_90_{folder}.csv"))
    
    # ==========================================================
    # VISUALIZATIONS
    # ==========================================================
    def plot_pc_heatmap(pc_name, save_name):
        temp_df = loadings_df[[pc_name]].copy()
        temp_df['metric'] = [f.rsplit('_', 1)[0] for f in temp_df.index]
        temp_df['hour'] = [int(f.rsplit('_', 1)[1]) for f in temp_df.index]
        
        heatmap_data = temp_df.pivot(index="metric", columns="hour", values=pc_name)
        
        plt.figure(figsize=(15, 7))
        sns.heatmap(heatmap_data, cmap="RdBu_r", center=0, annot=False, 
                   cbar_kws={'label': 'Loading (Correlation)'})
        plt.title(f"Feature Influence Map: {pc_name} - {folder}")
        plt.xlabel("Hour of Day (0-23)")
        plt.ylabel("Movement Metric")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, save_name), dpi=300)
        plt.close()  # Close to save memory
    
    # Plot first 4 PCs
    for i in range(1, min(5, n_components_90 + 1)):
        pc_name = f"PC{i}"
        plot_pc_heatmap(pc_name, f"heatmap_{pc_name}_interpretation_{folder}.png")
    
    # Scree Plot
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, len(explained_variance) + 1), explained_variance, 
            alpha=0.6, label="Individual")
    plt.step(range(1, len(explained_variance) + 1), cum_var, 
             where='mid', label="Cumulative", color='red')
    plt.axhline(y=0.90, color='black', linestyle='--', label="90% Threshold")
    plt.axvline(x=n_components_90, color='green', linestyle=':', 
                label=f'PC={n_components_90}')
    plt.title(f"Scree Plot - 90% Variance Threshold ({folder})")
    plt.xlabel("Principal Component")
    plt.ylabel("Explained Variance Ratio")
    plt.legend()
    plt.savefig(os.path.join(RESULTS_DIR, f"scree_plot_90_{folder}.png"), dpi=300)
    plt.close()
    
    print(f"Completed processing for {folder}. Results saved to: {RESULTS_DIR}")

print("\n🎉 All folders processed successfully!")