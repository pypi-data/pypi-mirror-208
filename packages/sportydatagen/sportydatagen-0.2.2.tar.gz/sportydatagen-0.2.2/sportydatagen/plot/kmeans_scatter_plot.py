"""KMmeans scatter plot for standard and PCA 2D data."""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans


def plot_kmeans_scatter(
    df_data: np.ndarray or pd.DataFrame,
    kmeans: KMeans,
    dot_size_for_scatter: int,
    dot_size_centroid: int,
    abscise: int,
    ordinate: int,
    output_file: str = None,
) -> plt:
    """Plot kmeans scatter plot.

    Args:
    ----
    df_data (numpy.ndarray or pd.DataFrame): Data to plot.
    kmeans (KMeans): Kmeans model.
    dot_size_for_scatter (int): Size of dots for scatter plot.
    dot_size_centroid (int): Size of dots for centroids.
    abscise (int): Abscise (label) of plot.
    ordinate (int): Ordinate (label) of plot.
    output_file (str, optional): Output file name.

    Returns:
    -------
    plt.figure (matplotlib.pyplot): Kmeans scatter plot.
    or
    None: If output_file is defined, save .png to disk.
    """
    x_label, y_label = None, None

    # Check if df_data is a dataframe
    if isinstance(df_data, pd.DataFrame):
        # Create x and y labels
        x_label = df_data.columns[abscise]
        y_label = df_data.columns[ordinate]
        # Convert to numpy array
        df_data = df_data.to_numpy()

    # Get unique labels
    unique_labels = np.unique(kmeans.labels_)

    # Get centroids of clusters
    centroids = kmeans.cluster_centers_

    # Plot clusters
    for cluster in unique_labels:
        plt.scatter(
            df_data[kmeans.labels_ == cluster, abscise],
            df_data[kmeans.labels_ == cluster, ordinate],
            s=dot_size_for_scatter,
            label=cluster,
        )
    # Plot centroids
    plt.scatter(
        centroids[:, abscise],
        centroids[:, ordinate],
        s=dot_size_centroid,
        color='k',
    )
    # Create title
    plt.title('Kmeans scatter plot')

    # Check if x and y labels are defined
    if not x_label and not y_label:
        # If not, use number
        x_label = kmeans.labels_[abscise]
        y_label = kmeans.labels_[ordinate]

    # Add x and y labels to plot
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Create legend
    plt.legend()

    # Save plot to disk
    if output_file is not None:
        plt.savefig(output_file)
        return None

    return plt
