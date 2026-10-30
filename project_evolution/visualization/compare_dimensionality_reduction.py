"""
Compare PCA, Kernel PCA, Sparse PCA, and UMAP embeddings for elephant 01fe.

Purpose
-------
Visualizes and compares the four dimensionality-reduction outputs already
generated for the 49-month, 120-feature movement matrix of elephant 01fe:

    - PCA (linear baseline, 17 components, published methodology)
    - Kernel PCA (RBF kernel, 17 components)
    - Sparse PCA (L1-regularized, 17 components)
    - UMAP (10 dimensions)

This script does NOT re-run any dimensionality reduction. It reads the
existing CSV outputs, verifies they describe the same 49 months in the
same order, and produces comparison figures. Spectral clustering on these
embeddings is a separate, later step and is intentionally not done here.

Inputs (read-only)
-------------------
    project_evolution/results/PCAVector/fe/01fe/pca_projected_features_90_01fe.csv
    project_evolution/results/AlternativeDimensionalityReduction/KernelPCA/kernelpca_features.csv
    project_evolution/results/AlternativeDimensionalityReduction/SparsePCA/sparsepca_features.csv
    project_evolution/results/AlternativeDimensionalityReduction/SparsePCA/sparsepca_loadings.csv
    project_evolution/results/AlternativeDimensionalityReduction/UMAP/umap_features.csv

Outputs
-------
    project_evolution/results/DimensionalityReductionVisualization/*.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR.parent / "results"
OUTPUT_DIR = RESULTS_DIR / "DimensionalityReductionVisualization"

PCA_FILE = RESULTS_DIR / "PCAVector" / "fe" / "01fe" / "pca_projected_features_90_01fe.csv"
KPCA_FILE = RESULTS_DIR / "AlternativeDimensionalityReduction" / "KernelPCA" / "kernelpca_features.csv"
SPCA_FEATURES_FILE = RESULTS_DIR / "AlternativeDimensionalityReduction" / "SparsePCA" / "sparsepca_features.csv"
SPCA_LOADINGS_FILE = RESULTS_DIR / "AlternativeDimensionalityReduction" / "SparsePCA" / "sparsepca_loadings.csv"
UMAP_FILE = RESULTS_DIR / "AlternativeDimensionalityReduction" / "UMAP" / "umap_features.csv"

DPI = 300

sns.set_theme(style="whitegrid")

# Fixed color per year so the same year is the same color across every figure.
YEAR_PALETTE = {
    2009: "#1f77b4",
    2010: "#ff7f0e",
    2011: "#2ca02c",
    2012: "#d62728",
    2013: "#9467bd",
}


# ---------------------------------------------------------------------
# Loading and validation
# ---------------------------------------------------------------------

def load_embedding(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{label} input file was not found: {path.resolve()}\n"
            "Generate it first (see project_evolution/dimensionality_reduction/)."
        )
    df = pd.read_csv(path, index_col=0)
    if df.empty:
        raise ValueError(f"{label} file is empty: {path.resolve()}")
    return df


def months_to_years(index: pd.Index) -> np.ndarray:
    return np.array([int(m.split("-")[0]) for m in index])


def validate_same_months(frames: dict[str, pd.DataFrame]) -> list[str]:
    """Ensure all four methods describe exactly the same 49 months, in order."""
    reference_name, reference_df = next(iter(frames.items()))
    reference_months = list(reference_df.index)
    for name, df in frames.items():
        if list(df.index) != reference_months:
            raise ValueError(
                f"Month index mismatch between '{reference_name}' and '{name}'. "
                "All dimensionality-reduction outputs must describe the same "
                "observations in the same order before they can be compared. "
                f"{reference_name} has {len(reference_months)} months, "
                f"{name} has {len(df.index)} months."
            )
    return reference_months


# ---------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------

def _point_colors(months: list[str]) -> list[str]:
    years = months_to_years(pd.Index(months))
    return [YEAR_PALETTE.get(y, "#777777") for y in years]


def _month_label(month: str) -> str:
    # "2009-07" -> "09-07" (drop the century for a compact point label)
    return month[2:]


def scatter_with_labels(ax, df: pd.DataFrame, x_col: str, y_col: str, months: list[str], title: str):
    colors = _point_colors(months)
    ax.scatter(df[x_col], df[y_col], c=colors, s=40, edgecolor="white", linewidth=0.5, zorder=3)
    for month, x, y in zip(months, df[x_col], df[y_col]):
        ax.annotate(
            _month_label(month),
            (x, y),
            fontsize=6,
            alpha=0.75,
            xytext=(3, 3),
            textcoords="offset points",
        )
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(title)


def add_year_legend(fig, loc="upper right"):
    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=8, label=str(year))
        for year, color in YEAR_PALETTE.items()
    ]
    fig.legend(handles=handles, title="Year", loc=loc, fontsize=8, title_fontsize=9)


def save_fig(fig, filename: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / filename
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("Saved:", out_path.resolve())


# ---------------------------------------------------------------------
# Individual method scatter plots
# ---------------------------------------------------------------------

def plot_pairwise(df: pd.DataFrame, months: list[str], col1: str, col2: str, col3: str, method_name: str, prefix: str):
    for other_col, suffix in [(col2, "2"), (col3, "3")]:
        fig, ax = plt.subplots(figsize=(9, 7))
        scatter_with_labels(ax, df, col1, other_col, months, f"{method_name}: {col1} vs {other_col}")
        add_year_legend(fig)
        save_fig(fig, f"{prefix}_{col1.lower()}_vs_{other_col.lower()}.png")


# ---------------------------------------------------------------------
# Sparse PCA loadings heatmap
# ---------------------------------------------------------------------

def plot_sparse_loadings_heatmap(loadings: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 22))
    sns.heatmap(
        loadings,
        cmap="RdBu_r",
        center=0,
        cbar_kws={"label": "Loading value"},
        ax=ax,
        yticklabels=True,
    )
    ax.set_title("Sparse PCA loading matrix (120 movement features x 17 components)")
    ax.set_xlabel("Component")
    ax.set_ylabel("Movement feature (metric_hour)")
    ax.tick_params(axis="y", labelsize=6)
    save_fig(fig, "07_sparsepca_loadings_heatmap.png")


# ---------------------------------------------------------------------
# Combined 2x2 comparison
# ---------------------------------------------------------------------

def plot_combined_comparison(pca, kpca, spca, umap, months):
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    scatter_with_labels(axes[0, 0], pca, "PC1", "PC2", months, "PCA (baseline)")
    scatter_with_labels(axes[0, 1], kpca, "KPCA1", "KPCA2", months, "Kernel PCA (RBF)")
    scatter_with_labels(axes[1, 0], spca, "SPCA1", "SPCA2", months, "Sparse PCA (L1)")
    scatter_with_labels(axes[1, 1], umap, "UMAP1", "UMAP2", months, "UMAP")

    fig.suptitle("Dimensionality reduction comparison — elephant 01fe, 49 months", fontsize=14)
    add_year_legend(fig, loc="lower right")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_fig(fig, "10_combined_comparison_2x2.png")


# ---------------------------------------------------------------------
# Temporal (chronological) trajectory plots
# ---------------------------------------------------------------------

def plot_temporal_trajectory(df: pd.DataFrame, x_col: str, y_col: str, months: list[str], method_name: str, filename: str):
    colors = _point_colors(months)
    fig, ax = plt.subplots(figsize=(10, 8))

    # Connect consecutive months in chronological order (the CSVs are
    # already sorted chronologically; order is preserved, not re-sorted).
    ax.plot(df[x_col], df[y_col], color="#999999", linewidth=0.8, alpha=0.6, zorder=1)
    ax.scatter(df[x_col], df[y_col], c=colors, s=45, edgecolor="white", linewidth=0.5, zorder=3)

    # Mark the first and last month so the chronological direction is clear.
    ax.scatter(df[x_col].iloc[0], df[y_col].iloc[0], facecolor="none", edgecolor="black", s=160, linewidth=1.5, zorder=4)
    ax.annotate("start: " + months[0], (df[x_col].iloc[0], df[y_col].iloc[0]), fontsize=7, xytext=(6, 6), textcoords="offset points")
    ax.scatter(df[x_col].iloc[-1], df[y_col].iloc[-1], facecolor="none", edgecolor="black", marker="s", s=160, linewidth=1.5, zorder=4)
    ax.annotate("end: " + months[-1], (df[x_col].iloc[-1], df[y_col].iloc[-1]), fontsize=7, xytext=(6, -10), textcoords="offset points")

    for month, x, y in zip(months, df[x_col], df[y_col]):
        ax.annotate(_month_label(month), (x, y), fontsize=5, alpha=0.6, xytext=(2, 2), textcoords="offset points")

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f"{method_name}: chronological trajectory (2009-07 → 2013-07)")
    add_year_legend(fig)
    save_fig(fig, filename)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    pca = load_embedding(PCA_FILE, "PCA")
    kpca = load_embedding(KPCA_FILE, "Kernel PCA")
    spca = load_embedding(SPCA_FEATURES_FILE, "Sparse PCA (features)")
    spca_loadings = load_embedding(SPCA_LOADINGS_FILE, "Sparse PCA (loadings)")
    umap_df = load_embedding(UMAP_FILE, "UMAP")

    months = validate_same_months({"PCA": pca, "Kernel PCA": kpca, "Sparse PCA": spca, "UMAP": umap_df})
    print(f"Validated {len(months)} matching months across all four methods: {months[0]} .. {months[-1]}")

    # 1-2. PCA
    plot_pairwise(pca, months, "PC1", "PC2", "PC3", "PCA (baseline)", "01_pca")

    # 3-4. Kernel PCA
    plot_pairwise(kpca, months, "KPCA1", "KPCA2", "KPCA3", "Kernel PCA (RBF)", "03_kernelpca")

    # 5-6. Sparse PCA
    plot_pairwise(spca, months, "SPCA1", "SPCA2", "SPCA3", "Sparse PCA (L1)", "05_sparsepca")

    # 7. Sparse PCA loadings heatmap
    plot_sparse_loadings_heatmap(spca_loadings)

    # 8-9. UMAP
    plot_pairwise(umap_df, months, "UMAP1", "UMAP2", "UMAP3", "UMAP", "08_umap")

    # 10. Combined 2x2 comparison
    plot_combined_comparison(pca, kpca, spca, umap_df, months)

    # 11-14. Temporal trajectories (one per method)
    plot_temporal_trajectory(pca, "PC1", "PC2", months, "PCA", "11_temporal_pca.png")
    plot_temporal_trajectory(kpca, "KPCA1", "KPCA2", months, "Kernel PCA", "12_temporal_kernelpca.png")
    plot_temporal_trajectory(spca, "SPCA1", "SPCA2", months, "Sparse PCA", "13_temporal_sparsepca.png")
    plot_temporal_trajectory(umap_df, "UMAP1", "UMAP2", months, "UMAP", "14_temporal_umap.png")

    print(f"\nAll figures saved to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
