# Alternative Dimensionality Reduction

This folder contains experiments for comparing alternative dimensionality-reduction methods with the PCA baseline used in the published methodology.

## Methods

- UMAP (`umap_reduction.py`) — implemented
- Kernel PCA (`kernel_pca.py`) — implemented, RBF kernel, n_components=17 to match the linear PCA baseline
- Sparse PCA (`sparse_pca.py`) — implemented, n_components=17 to match the linear PCA baseline

All three scripts currently process a single elephant (01fe), matching the
primary subject used in the original paper, so results stay comparable to
the published PCA + spectral clustering findings rather than introducing a
second experimental variable (which elephant).

## Planned workflow

120D monthly movement feature matrix
→ Standardization
→ Dimensionality reduction
→ Spectral clustering
→ Cluster evaluation and comparison

The same 120D feature matrix and downstream spectral-clustering framework should be used as consistently as possible across methods so that the dimensionality-reduction method is the main experimental difference.

## Scope

This folder is for the new dimensionality-reduction experiments. The existing Elephant 3 directory is not modified by these experiments.
