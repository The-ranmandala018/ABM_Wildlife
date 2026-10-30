# Research Workspace

This folder is the single, scalable workspace for all current and future
development work on the elephant movement seasonality project: machine
learning experiments, dimensionality reduction, clustering, feature
engineering, preprocessing, model development/evaluation, visualization, and
new research directions as they come up.

It replaces ad-hoc numbered folders for anything new going forward. Existing
numbered folders at the repository root (`01_data_quality/` ... 
`06_environmental_analysis/`) are left in place for now and are not affected
by this workspace; they may be migrated in here later, one area at a time.

## Structure

```
research/
├── README.md                      this file
├── data_quality/                  anomaly detection, cleaning
├── feature_engineering/           movement feature extraction (NSD, step
│                                   length, speed, turning angle, hourly
│                                   aggregation)
├── dimensionality_reduction/      PCA baseline + alternatives (Kernel PCA,
│                                   Sparse PCA, UMAP, ...)
├── clustering/                    spectral clustering, eigen-gap analysis,
│                                   and any future clustering methods
├── visualization/                 trajectory plots, cluster mobility
│                                   profiles, heatmaps
├── environmental_analysis/        weather/NDVI/solar-time integration
└── results/                       gitignored. Server-only generated
                                    outputs and symlinks into the raw/
                                    intermediate datasets. Never pushed to
                                    GitHub.
```

## Adding a new research area

1. Create a new subfolder under `research/` named after the area (e.g.
   `research/model_benchmarking/`).
2. Add a `README.md` inside it describing the method(s), inputs, and
   outputs, following the style of `dimensionality_reduction/README.md`.
3. If the scripts need generated data or output storage, write to
   `research/results/<area_name>/...` — this path is gitignored, so large
   files never get pushed.
4. No renumbering or restructuring of other folders is needed — this layout
   is designed to grow by addition, not reorganization.

## Data and environment notes

- Raw GPS/climate datasets stay on the server only (`Elephant/`, `Datasets/`,
  etc.) and are referenced via symlinks under `research/results/`, never
  copied into this workspace or pushed to GitHub.
- `research/.venv/` is a dedicated Python virtual environment for this
  workspace, isolated from the shared conda environment used elsewhere in
  the repo (which has TensorFlow installed for `GenAI_Model/`). Some
  packages used here (`umap-learn` → `numba`/`llvmlite`) segfault when
  TensorFlow is loaded in the same process due to a native LLVM/XLA symbol
  conflict, hence the isolated venv. Activate it before running any script
  in this workspace:
  ```
  source research/.venv/bin/activate
  ```
  `.venv/` is gitignored and never pushed.
