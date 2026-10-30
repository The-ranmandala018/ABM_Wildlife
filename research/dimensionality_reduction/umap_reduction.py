"""
UMAP dimensionality reduction for the 120D monthly elephant movement features.

Purpose
-------
This script is the UMAP alternative to the PCA step in the main workflow.

Pipeline:
    120D monthly feature matrix
        -> standardization
        -> UMAP
        -> reduced representation

The reduced representation can then be supplied to the existing
spectral-clustering workflow.

Notes
-----
- This is an initial experiment script.
- Input/output paths should be adapted after confirming the exact
  120D feature-matrix location and format in the current repository.
- The Elephant 3 directory is not used or modified here.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

try:
    import umap
except ImportError as exc:
    raise ImportError(
        "UMAP is not installed. Install it with: pip install umap-learn"
    ) from exc


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Update this path after confirming the exact 120D feature-matrix file.
INPUT_FILE = Path("../results/120D/fe/01fe/feature_matrix_for_clustering.csv")

# Output directory for the new UMAP experiment.
OUTPUT_DIR = Path("../results/AlternativeDimensionalityReduction/UMAP")

# Number of dimensions in the UMAP representation.
N_COMPONENTS = 10

# UMAP neighborhood size.
N_NEIGHBORS = 10

# Minimum distance between points in the reduced space.
MIN_DIST = 0.1

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

# UMAP requires numeric input. Keep identifier columns so that the
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
        "Handle missing values before UMAP."
    )


# ---------------------------------------------------------------------
# Standardization
# ---------------------------------------------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# ---------------------------------------------------------------------
# UMAP
# ---------------------------------------------------------------------

reducer = umap.UMAP(
    n_components=N_COMPONENTS,
    n_neighbors=N_NEIGHBORS,
    min_dist=MIN_DIST,
    random_state=RANDOM_STATE,
)

X_umap = reducer.fit_transform(X_scaled)

print("UMAP output shape:", X_umap.shape)


# ---------------------------------------------------------------------
# Save reduced representation
# ---------------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

umap_columns = [
    f"UMAP{i + 1}"
    for i in range(N_COMPONENTS)
]

umap_df = pd.DataFrame(
    X_umap,
    columns=umap_columns,
)

# Put original identifiers first when they exist.
if id_columns:
    output_df = pd.concat(
        [data[id_columns].reset_index(drop=True), umap_df],
        axis=1,
    )
else:
    output_df = umap_df

output_file = OUTPUT_DIR / "umap_features.csv"
output_df.to_csv(output_file, index=False)

print("Saved:", output_file.resolve())
