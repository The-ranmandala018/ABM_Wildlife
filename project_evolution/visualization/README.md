# Dimensionality Reduction Visualization

`compare_dimensionality_reduction.py` reads the four already-generated
dimensionality-reduction outputs for elephant 01fe (PCA, Kernel PCA, Sparse
PCA, UMAP) and produces comparison figures. It does not re-run any
reduction method and does not perform clustering.

## What each visualization shows

| File | What it shows |
| --- | --- |
| `01_pca_pc1_vs_pc2.png`, `01_pca_pc1_vs_pc3.png` | The published linear PCA baseline: each point is one month, projected onto its top 2-3 principal components. |
| `03_kernelpca_kpca1_vs_kpca2.png`, `03_kernelpca_kpca1_vs_kpca3.png` | The same 49 months projected by Kernel PCA (RBF kernel). |
| `05_sparsepca_spca1_vs_spca2.png`, `05_sparsepca_spca1_vs_spca3.png` | The same 49 months projected by Sparse PCA. |
| `07_sparsepca_loadings_heatmap.png` | Which of the 120 original hour/metric features feed into each Sparse PCA component. Most cells are exactly zero (white); a colored cell means that feature contributes to that component. |
| `08_umap_umap1_vs_umap2.png`, `08_umap_umap1_vs_umap3.png` | The same 49 months projected by UMAP. |
| `10_combined_comparison_2x2.png` | All four methods' first two dimensions side by side, same year-color scheme, for direct visual comparison. |
| `11_temporal_pca.png`, `12_temporal_kernelpca.png`, `13_temporal_sparsepca.png`, `14_temporal_umap.png` | Each method's embedding with a line connecting the months in chronological order (not spatial distance), so you can see how the representation moves month-to-month across the 2009-07 to 2013-07 span. Start and end months are marked with a circle and a square. |

In every figure, point color = year (fixed mapping, same colors in every
plot) and point labels are `YY-MM` (e.g. `09-07` = July 2009).

## How to interpret each plot

- **PCA, Kernel PCA, Sparse PCA scatter plots**: distance between two
  points is this method's notion of how different those two months'
  movement behavior was. Points that cluster together are months the
  method considers behaviorally similar; this is the same structure that
  spectral clustering later groups into seasons.
- **Sparse PCA loadings heatmap**: reads top-to-bottom as "which hour of
  which metric", left-to-right as component. SPCA1's near-total reliance
  on `nsd_mean` across all 24 hours mirrors the published paper's finding
  that net squared displacement is the primary seasonal discriminator (PC1
  in the paper) -- but here it is visibly isolated to one component instead
  of blended across PC1-PC3.
- **UMAP scatter plots**: UMAP preserves *local* neighborhood structure,
  not global distances or variance. Two points close together are mutual
  near-neighbors in the original 120D space; the distance between two
  far-apart clusters is not meaningful (unlike PCA/Kernel PCA, where axis
  distances relate to variance).
- **Temporal trajectory plots**: a relatively short, tangled line (points
  revisiting the same region) indicates the behavioral state repeats
  across years for that part of the calendar; a long jump indicates an
  abrupt behavioral change between consecutive months.
- **Combined 2x2**: look for whether the same months cluster together
  across all four panels. If they do, the four methods agree on the
  behavioral structure despite being mathematically very different; where
  they disagree is where the choice of reduction method matters.

## Why PCA, Kernel PCA, Sparse PCA, and UMAP look different

All four start from the same standardized 120D monthly feature matrix, but:

- **PCA** finds the directions of maximum *linear* variance. It is the
  published baseline and assumes the important structure is captured by
  linear combinations of the original features.
- **Kernel PCA** applies an RBF kernel before finding directions of
  variance, so it can capture *non-linear* relationships PCA cannot. If
  the data were strongly non-linear, Kernel PCA's first components would
  show a much higher explained-share than linear PCA's; the companion
  results document shows this is not really the case here (Kernel PCA's
  eigenvalue spread is nearly flat), which is itself evidence the linear
  PCA baseline was not missing major non-linear structure.
- **Sparse PCA** adds an L1 penalty that forces most loadings to exactly
  zero, trading some variance-explaining power for components that are
  each tied to a small number of original features -- useful for
  interpretation, not for maximizing variance captured.
- **UMAP** does not decompose variance at all. It builds a nearest-neighbor
  graph in the original 120D space and optimizes a low-dimensional layout
  that preserves local neighborhoods. It is a fundamentally different kind
  of algorithm (manifold learning, not a matrix factorization), which is
  why its axes have no variance-based interpretation.

## Why UMAP has no explained-variance plot

Explained variance (the scree plots PCA/Kernel PCA can produce) comes from
an eigenvalue decomposition: each component has an eigenvalue, and
"explained variance" is that eigenvalue's share of the total. UMAP does not
compute eigenvalues or decompose variance -- it directly optimizes an
embedding layout to preserve neighbor relationships, via gradient descent
on a cross-entropy-like loss, not a decomposition. There is no quantity in
UMAP's output that corresponds to "how much variance this dimension
explains", so no analogous plot exists for it.

## What can and cannot be concluded from these visualizations

**Can conclude:**
- Whether the four methods broadly agree or disagree on which months look
  behaviorally similar (visual clustering structure).
- Which original hour/metric features drive each Sparse PCA component
  (directly, from the loadings heatmap).
- Whether a method's first two dimensions separate the data into visually
  distinct groups at all, or produce a single undifferentiated blob.

**Cannot conclude:**
- Which clustering (k=2, k=3, k=4, ...) each method would produce, or
  whether it would match the published wet/dry/transitional seasons --
  that requires actually running spectral clustering on each embedding,
  which this task deliberately does not do.
- That visual separation in a 2D scatter plot is statistically significant
  or ecologically meaningful on its own; it is a qualitative first look,
  not a validated result.
- That one method is "better" than another from these plots alone --
  Kernel PCA's flat eigenvalue spectrum and UMAP's different axis meaning
  are evidence, not proof, and the real test is downstream clustering
  quality against the paper's established seasons.

## How to run

```
cd project_evolution/visualization
python3 compare_dimensionality_reduction.py
```

Requires `pandas`, `numpy`, `matplotlib`, `seaborn` (all available in the
system Python already used for `kernel_pca.py`/`sparse_pca.py`; the
dedicated `project_evolution/.venv` used for UMAP generation is not needed
here, since this script only reads UMAP's already-generated CSV, it does
not import `umap-learn`).

All 14 output PNGs are written to
`project_evolution/results/DimensionalityReductionVisualization/` (300 DPI,
gitignored along with the rest of `project_evolution/results/`).
