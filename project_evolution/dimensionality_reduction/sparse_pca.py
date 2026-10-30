"""
Sparse PCA dimensionality reduction for the 120D monthly elephant movement features.

Purpose
-------
This script is the Sparse PCA alternative to the linear PCA step used in the
published methodology (03_pca/pca.py). Ordinary PCA components are dense
linear combinations of all 120 hourly features, which can make ecological
interpretation harder (every hour of every metric contributes a little).
Sparse PCA instead encourages each component to load heavily on only a few
hour/metric combinations, which may produce more directly interpretable
"behavioral signatures" than the dense PCA loadings reported in the paper.

n_components is kept at 17, matching the components linear PCA retained for
>=90% explained variance, so the dimensionality-reduction method is the main
experimental difference between this script and the original PCA step.

Pipeline:
    120D monthly feature matrix
        -> standardization
        -> Sparse PCA
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
from sklearn.decomposition import SparsePCA


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Update this path after confirming the exact 120D feature-matrix file.
INPUT_FILE = Path("../results/120D/fe/01fe/feature_matrix_for_clustering.csv")

# Output directory for the new Sparse PCA experiment.
OUTPUT_DIR = Path("../results/AlternativeDimensionalityReduction/SparsePCA")

# Number of components, matching the 17 components retained by linear PCA
# for >=90% explained variance in the original paper, for a fair comparison.
N_COMPONENTS = 17

# Sparsity-controlling regularization strength. Higher alpha -> sparser
# components (more loadings pushed to exactly zero).
ALPHA = 1.0

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

# Sparse PCA requires numeric input. Keep identifier columns so that the
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
        "Handle missing values before Sparse PCA."
    )


# ---------------------------------------------------------------------
# Standardization
# ---------------------------------------------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# ---------------------------------------------------------------------
# Sparse PCA
# ---------------------------------------------------------------------

n_components = min(N_COMPONENTS, X_scaled.shape[0] - 1, X_scaled.shape[1])
if n_components != N_COMPONENTS:
    print(
        f"Requested N_COMPONENTS={N_COMPONENTS} exceeds what the data "
        f"supports; using n_components={n_components} instead."
    )

spca = SparsePCA(
    n_components=n_components,
    alpha=ALPHA,
    random_state=RANDOM_STATE,
)

X_spca = spca.fit_transform(X_scaled)

print("Sparse PCA output shape:", X_spca.shape)

# Sparse PCA components (loadings) show which hour/metric combinations
# dominate each component, analogous to the PC1/PC2/PC3 loading heatmaps
# in the original paper, but with most entries pushed to exactly zero.
components_df = pd.DataFrame(
    spca.components_.T,
    index=feature_columns,
    columns=[f"SPCA{i + 1}" for i in range(n_components)],
)

nonzero_share = (components_df != 0).mean()
print("Fraction of non-zero loadings per component:")
print(nonzero_share)


# ---------------------------------------------------------------------
# Save reduced representation
# ---------------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

spca_columns = [
    f"SPCA{i + 1}"
    for i in range(X_spca.shape[1])
]

spca_df = pd.DataFrame(
    X_spca,
    columns=spca_columns,
)

# Put original identifiers first when they exist.
if id_columns:
    output_df = pd.concat(
        [data[id_columns].reset_index(drop=True), spca_df],
        axis=1,
    )
else:
    output_df = spca_df

output_file = OUTPUT_DIR / "sparsepca_features.csv"
output_df.to_csv(output_file, index=False)

print("Saved:", output_file.resolve())

# Save the component loadings for interpretation, mirroring the
# pca_loadings_90.csv file produced by the original PCA step.
loadings_file = OUTPUT_DIR / "sparsepca_loadings.csv"
components_df.to_csv(loadings_file)
print("Saved:", loadings_file.resolve())
