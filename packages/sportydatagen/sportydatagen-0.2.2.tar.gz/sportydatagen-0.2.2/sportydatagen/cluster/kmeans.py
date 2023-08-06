"""K-Means Clustering with standard and PCA data."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder


def encode_labels(
    df_data: pd.DataFrame,
    encode_columns: list = None,
) -> pd.DataFrame:
    """Encode target labels with value between 0 and n_classes.

    Args:
    ----
    df_data (pd.DataFrame): df with data to encode.
    encode_columns (list, optional): List of columns to encode.
        Defaults to None. Automatically encodes all string columns.

    Returns:
    -------
    pd.DataFrame: df with encoded string data.
    """
    # If no columns are specified, encode all string columns
    if encode_columns is None:
        # Find all string columns
        encode_columns = df_data.loc[
            :, (df_data.applymap(type) == str).all(0),
        ].columns
        # Create list from pandas.core.indexes.base.Index
        encode_columns = list(encode_columns)
    for column in encode_columns:
        try:
            encoder = LabelEncoder()
            # Try to encode the column
            df_data[column] = encoder.fit_transform(df_data[column])
        except ValueError:
            # If encoding fails, raise error
            err_msg = f'Could not encode column {column}'
            raise ValueError from ValueError(err_msg)
    # Return the encoded dataframe
    return df_data


def kmeans_info(data: pd.DataFrame, kmeans: KMeans) -> dict:
    """Return information about the KMeans object.

    Args:
    ----
    data (pd.DataFrame): Data used for clustering.
    kmeans (KMeans): KMeans object.

    Returns:
    -------
    dict: Dictionary with information about the KMeans object.
    """
    # Create dictionary with information about the KMeans object
    return {
        'cluster_centers': kmeans.cluster_centers_,
        'inertia': kmeans.inertia_,
        'n_iter': kmeans.n_iter_,
        'n_init': kmeans.n_init,
        'max_iter': kmeans.max_iter,
        'tol': kmeans.tol,
        'verbose': kmeans.verbose,
        'copy_x': kmeans.copy_x,
        'algorithm': kmeans.algorithm,
        'score': kmeans.score(data),
        'get_feature_names_out': kmeans.get_feature_names_out(),
    }


def cluster_kmeans(
    df_data: pd.DataFrame,
    n_clusters: int,
    column_name: str,
    random_state: int = 0,
    n_components: int or None = None,
    output_file: str = None,
) -> pd.DataFrame and KMeans or None:
    """Cluster data using K-Means algorithm.

    Args:
    ----
    df_data (pd.DataFrame): Data to cluster.
    n_clusters (int): Number of clusters to use.
    column_name (str): Name of the column to add to the
        dataframe with the cluster information.
    random_state (int, optional): Random state for
        reproducibility.
    n_components (None or int): Triggers PCA
        Defaults to None.
    output_file (str, optional): Output file name.
        Defaults to None.

    Returns:
    -------
    pd.DataFrame: dataframe with cluster column and
    sklearn.cluster._kmeans.KMeans: object
        containing data about the clustering.

    and (optional) if (PCA) n_components is not None:
    pca_data (np.array): PCA data transformation

    or
    None: If output_file is set, save .csv to disk
    """
    # Copy the data to avoid changing the original
    df_data = df_data.copy()
    fit_data = df_data

    if n_components is not None:
        # Create the PCA model
        pca = PCA(n_components=n_components)
        # PCA data transformation
        fit_data = pca.fit_transform(df_data)

    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        random_state=random_state,
        n_init='auto',
    ).fit(fit_data)

    # attach predicted cluster to original data
    df_data[column_name] = kmeans.labels_

    if output_file is None and n_components is not None:
        return df_data, kmeans, fit_data
    if output_file is None:
        return df_data, kmeans

    df_data.to_csv(output_file, sep=';', index=False)
    return None


def kmeans_pca_analysis(
    df_data: pd.DataFrame,
        n_clusters: int,
) -> pd.DataFrame:
    """Cluster data with KMeans and PCA.

    Args:
    ----
    df_data (pd.DataFrame): Data to cluster.
    n_clusters (int): Number of clusters to use.

    Returns:
    -------
    pca_statistics (pd.DataFrame): Dataframe with multiple
        cluster columns.
    """
    # Cluster data with KMeans
    df_kmeans, _ = cluster_kmeans(
        df_data=df_data, n_clusters=n_clusters, column_name='standard_KMeans',
    )

    dict_pca = {}
    for index in range(1, len(df_data.columns)):
        # Create the column name
        column_name = 'pca' + str(index) + '_KMeans'

        # Cluster PCA data with KMeans
        df_data, kmeans, _ = cluster_kmeans(
            df_data=df_data,
            n_clusters=n_clusters,
            n_components=index,
            column_name=column_name,
        )

        # Create a new column with 1 if the cluster from
        # standard_data and PCA_data after Kmeans are the same
        df_data['test_similarity'] = np.where(
            (df_kmeans['standard_KMeans'] == df_data[column_name]),
            1, 0)
        # Count values in test_similarity column
        dict_pca[column_name] = \
            len(df_data) - (df_data['test_similarity']).sum()

    # Create a dataframe with the results
    pca_statistics = pd.DataFrame.from_dict(
        dict_pca, orient='index', columns=['unmatching_values'],
    )
    # Calculate the percentage of unmatching values
    pca_statistics['percentage'] = pca_statistics['unmatching_values'] / len(
        df_data,
    )
    # Format the percentage column
    pca_statistics['%'] = pca_statistics['percentage'].map(
        lambda x: f'{x:.2%}',
    )

    # Return the dataframe
    return pca_statistics
