"""
Kernel PCA dimensionality reduction for the 120D monthly elephant movement features.

Purpose
-------
This script is the Kernel PCA alternative to the linear PCA step used in the
published methodology (03_pca/pca.py). Linear PCA retained 17 components to
reach >=90% explained variance; Kernel PCA is applied here with the same
n_components=17 so the dimensionality-reduction method is the main
experimental difference between this script and the original PCA step.

Pipeline:
    120D monthly feature matrix
        -> standardization
        -> Kernel PCA (RBF kernel)
        -> reduced representation

The reduced representation can then be supplied to the existing
spectral-clustering workflow, exactly as the linear PCA output is.

Notes
-----
- This follows the same elephant/scope convention as umap_reduction.py: a single
  elephant (01fe), matching the primary subject used in the original paper.
- Input/output paths should be adapted after confirming the exact
  120D feature-matrix location and format in the current repository.
- The Elephant 3 directory is not used or modified here.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import KernelPCA


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Update this path after confirming the exact 120D feature-matrix file.
INPUT_FILE = Path("../results/120D/fe/01fe/feature_matrix_for_clustering.csv")

# Output directory for the new Kernel PCA experiment.
OUTPUT_DIR = Path("../results/AlternativeDimensionalityReduction/KernelPCA")

# Number of components, matching the 17 components retained by linear PCA
# for >=90% explained variance in the original paper, for a fair comparison.
N_COMPONENTS = 17

# Kernel PCA kernel choice. RBF is used to capture non-linear structure that
# linear PCA cannot, which is the specific limitation this experiment probes.
KERNEL = "rbf"

# Kernel coefficient for 'rbf'. None lets scikit-learn use 1 / n_features.
GAMMA = None

# Reproducibility.
RANDOM_STATE = 42


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input feature matrix was not found: {INPUT_FILE.resolve()}\n"
        "Confirm the location of the 120D feature matrix before running."
    )

data = pd.read_csv(INPUT_FILE)

print("Input shape:", data.shape)
print("Columns:", list(data.columns))


# ---------------------------------------------------------------------
# Separate identifiers from numeric features
# ---------------------------------------------------------------------

# Kernel PCA requires numeric input. Keep identifier columns so that the
# resulting reduced data can be linked back to the corresponding month.
id_columns = [
    column
    for column in data.columns
    if not pd.api.types.is_numeric_dtype(data[column])
]

feature_columns = [
    column
    for column in data.columns
    if pd.api.types.is_numeric_dtype(data[column])
]

if not feature_columns:
    raise ValueError("No numeric feature columns were found.")

X = data[feature_columns].copy()

print("Identifier columns:", id_columns)
print("Number of numeric features:", len(feature_columns))


# ---------------------------------------------------------------------
# Handle missing values
# ---------------------------------------------------------------------

if X.isna().any().any():
    raise ValueError(
        "The feature matrix contains missing values. "
        "Handle missing values before Kernel PCA."
    )


# ---------------------------------------------------------------------
# Standardization
# ---------------------------------------------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# ---------------------------------------------------------------------
# Kernel PCA
# ---------------------------------------------------------------------

n_components = min(N_COMPONENTS, X_scaled.shape[0] - 1, X_scaled.shape[1])
if n_components != N_COMPONENTS:
    print(
        f"Requested N_COMPONENTS={N_COMPONENTS} exceeds what the data "
        f"supports; using n_components={n_components} instead."
    )

kpca = KernelPCA(
    n_components=n_components,
    kernel=KERNEL,
    gamma=GAMMA,
    random_state=RANDOM_STATE,
)

X_kpca = kpca.fit_transform(X_scaled)

print("Kernel PCA output shape:", X_kpca.shape)

# Kernel PCA does not have a direct explained-variance-ratio like linear PCA,
# but the eigenvalues of the centered kernel matrix give an analogous
# diagnostic of how much structure each component captures.
eigenvalues = getattr(kpca, "eigenvalues_", None)
if eigenvalues is not None:
    total = np.sum(np.abs(eigenvalues))
    explained_share = np.abs(eigenvalues) / total if total > 0 else eigenvalues
    print("Kernel PCA eigenvalues (first 5):", eigenvalues[:5])
    print("Approximate explained share (first 5):", explained_share[:5])


# ---------------------------------------------------------------------
# Save reduced representation
# ---------------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

kpca_columns = [
    f"KPCA{i + 1}"
    for i in range(X_kpca.shape[1])
]

kpca_df = pd.DataFrame(
    X_kpca,
    columns=kpca_columns,
)

# Put original identifiers first when they exist.
if id_columns:
    output_df = pd.concat(
        [data[id_columns].reset_index(drop=True), kpca_df],
        axis=1,
    )
else:
    output_df = kpca_df

output_file = OUTPUT_DIR / "kernelpca_features.csv"
output_df.to_csv(output_file, index=False)

print("Saved:", output_file.resolve())

# Save the eigenvalue diagnostic alongside the projected features, for
# comparison against the linear PCA scree plot.
if eigenvalues is not None:
    eigenvalues_df = pd.DataFrame(
        {
            "component": [f"KPCA{i + 1}" for i in range(len(eigenvalues))],
            "eigenvalue": eigenvalues,
        }
    )
    eigenvalues_file = OUTPUT_DIR / "kernelpca_eigenvalues.csv"
    eigenvalues_df.to_csv(eigenvalues_file, index=False)
    print("Saved:", eigenvalues_file.resolve())
