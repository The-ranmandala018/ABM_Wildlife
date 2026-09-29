import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Path setup (as per your structure)
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, '..', 'segments', 'fe', '01fe_with_segments.csv')

def plot_individual_outliers(path):
    df = pd.read_csv(path)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Create a grid of plots
    num_cols = len(numeric_cols)
    cols_per_row = 3
    rows = (num_cols // cols_per_row) + (num_cols % cols_per_row > 0)
    
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(15, rows * 4))
    axes = axes.flatten() # Flatten to 1D array for easy looping

    for i, col in enumerate(numeric_cols):
        sns.boxplot(y=df[col], ax=axes[i], color='skyblue')
        axes[i].set_title(f'Outliers in {col}')
        axes[i].set_ylabel('Value')
        
    # Remove empty subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

plot_individual_outliers(file_path)