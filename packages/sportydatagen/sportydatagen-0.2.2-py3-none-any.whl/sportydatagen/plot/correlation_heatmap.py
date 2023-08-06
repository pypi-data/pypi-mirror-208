"""Correlation heatmap plot."""

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def plot_correlation_heatmap(
    dataframe: pd.DataFrame,
    hm_length: int,
    hm_width: int,
    output_file: str = None,
) -> plt.figure:
    """Plot correlation heatmap of data.

    Args:
    ----
    dataframe (pd.DataFrame): df to plot
        correlation heatmap for.
    hm_length (int): Length of heatmap.
    hm_width (int): Width of heatmap.
    output_file (str, optional): Output file name.

    Returns:
    -------
    plt.figure (matplotlib.pyplot): Correlation heatmap.
    or
    None: If output_file is defined, save .png to disk.
    """
    # Check the correlation of the features
    dataframe = dataframe.drop(
        ['index', 'file_name', 'merged_from'], axis=1, errors='ignore',
    )
    # Calculate correlations
    correlation = dataframe.corr(numeric_only=True)
    # Plot figure size
    plt.figure(figsize=(hm_length, hm_width))
    # Plot heatmap
    sns.heatmap(correlation, vmax=1, square=True, annot=True, cmap='viridis')
    # Add title
    plt.title('Correlation between different features')

    # Ff output_file is not defined, return plot
    if output_file is None:
        return plt

    # If output file is defined, save to file
    plt.savefig(output_file)
    return None
