# Clustering

Reserved for future work in this workspace: spectral clustering,
sigma-sweep eigen-gap analysis, and any additional clustering methods used
to validate results from `dimensionality_reduction/`.

The existing implementation lives at `04_spectral_clustering/`
(repository root: `spectralClustering.py`, `PCAspectral.py`) and has not
been migrated here yet. This folder will hold new or migrated clustering
scripts as that work resumes — in particular, applying spectral clustering
to the Kernel PCA / Sparse PCA / UMAP outputs produced in
`dimensionality_reduction/` for comparison against the published PCA
baseline.
