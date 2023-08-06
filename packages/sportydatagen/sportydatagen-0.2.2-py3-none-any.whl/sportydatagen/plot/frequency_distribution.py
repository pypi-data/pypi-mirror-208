"""Plot frequency distribution of data."""

import pandas as pd
from matplotlib import pyplot as plt


def plot_frequency_distribution(
    df_data: pd.DataFrame,
    output_file: str = None,
) -> plt.figure or None:
    """Plot frequency distribution of data.

    Args:
    ----
    df_data (pd.DataFrame): Dataframe to plot.
    output_file (str, optional): Output file name.
        Defaults to None.

    Returns:
    -------
    plt.figure: Frequency distribution histogram.
    None: If output_file is defined, save .png to disk.
    """
    plt.style.use('seaborn-whitegrid')
    df_data.hist(bins=18, figsize=(60, 40), color='lightblue', edgecolor='red')
    plt.title('Frequency distribution histogram')
    # Show plot
    if output_file is None:
        return plt

    # If output file is defined, save to file
    plt.savefig(output_file)
    return None
