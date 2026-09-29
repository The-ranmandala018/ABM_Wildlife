# Alternative Dimensionality Reduction

This folder contains experiments for comparing alternative dimensionality-reduction methods with the PCA baseline used in the published methodology.

## Methods

- UMAP
- Kernel PCA
- Sparse PCA

## Planned workflow

120D monthly movement feature matrix
→ Standardization
→ Dimensionality reduction
→ Spectral clustering
→ Cluster evaluation and comparison

The same 120D feature matrix and downstream spectral-clustering framework should be used as consistently as possible across methods so that the dimensionality-reduction method is the main experimental difference.

## Scope

This folder is for the new dimensionality-reduction experiments. The existing Elephant 3 directory is not modified by these experiments.
