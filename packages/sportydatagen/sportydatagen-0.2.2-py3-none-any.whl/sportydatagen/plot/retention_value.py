"""Retention value plot for PCA model."""

import numpy as np
from matplotlib import pyplot as plt
from sklearn import decomposition


def plot_retention_value(
    pca: decomposition.PCA,
    output_file: str = None,
) -> plt.figure or None:
    """Plot retention value of PCA model.

    Args:
    ----
    pca (decomposition.PCA):
        PCA model
    output_file (str, optional):
        Output file name.

    Returns:
    -------
    plt.figure (matplotlib.pyplot):
        Plot of retention value
    or
    None:
        If output_file is defined, save .png to disk
    """
    retention_value = pca.explained_variance_ / np.sum(pca.explained_variance_)
    cumulative_retention = np.cumsum(retention_value)

    plt.plot(cumulative_retention)
    plt.grid()
    plt.xlabel('n_components')
    plt.locator_params(axis='x', integer=True, tight=True)
    plt.ylabel('Retention value on scale of 1')
    plt.title('PCA retention value')

    # Save plot to disk
    if output_file is not None:
        plt.savefig(output_file)
        return None

    return plt
