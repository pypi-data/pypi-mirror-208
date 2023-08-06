"""Return random data from extracted features."""
import pandas as pd


def return_number_random_data(
    filepath: str,
    random_size: int,
    random_state: int = 1,
) -> pd.DataFrame:
    """Return a number of random data from extracted features.

    Args:
    ----
    filepath (str): Path where the extracted features are stored.
    random_size (int): Number of random data to return.
    random_state (int): Random state for reproducibility.

    Returns:
    -------
    pd.DataFrame: Random data from extracted features.
    """
    # Pandas read csv
    read_df_tcx_csv = pd.read_csv(
        filepath_or_buffer=filepath,
        sep=';',
        index_col='index',
    )

    # Check if random_size is larger than the number of rows in .csv
    if random_size > len(read_df_tcx_csv):
        error_message = 'random_size is larger than nO. of rows in .csv'
        raise ValueError(error_message)

    return read_df_tcx_csv.sample(n=random_size, random_state=random_state)


def return_percent_random_data(
    filepath: str,
    random_percent: float,
    random_state: int = 1,
) -> pd.DataFrame:
    """Return a percent of random data from extracted features.

    Args:
    ----
    filepath (str): Path where the extracted features are stored.
    random_percent (float): Percent of random data to return.
    random_state (int): Random state for reproducibility.

    Returns:
    -------
    pd.DataFrame: Random data from extracted features.
    """
    # Pandas read csv
    read_df_tcx_csv = pd.read_csv(
        filepath_or_buffer=filepath,
        sep=';',
        index_col='index',
    )

    # Check if random_percent is larger than 1
    if random_percent > 1:
        error_message = 'random_percent is larger than 1'
        raise ValueError(error_message)

    return read_df_tcx_csv.sample(
        frac=random_percent,
        random_state=random_state,
    )


def return_condition_random_data(
    filepath: str,
    random_size: int = 10,
    random_state: int = 1,
    activity_type: str = 'any',
    min_total_distance: float = 0,
    max_total_distance: float = 999999,
    min_duration: float = 0,
    max_duration: float = 99999,
    min_calories: float = 0,
    max_calories: float = 99999,
    min_hr_avg: float = 0,
    max_hr_avg: float = 999,
    min_hr_min: float = 0,
    max_hr_min: float = 999,
    min_hr_max: float = 0,
    max_hr_max: float = 999,
    min_altitude_avg: float = 0,
    max_altitude_avg: float = 9999,
    min_altitude_min: float = 0,
    max_altitude_min: float = 9999,
    min_altitude_max: float = 0,
    max_altitude_max: float = 9999,
    min_ascent: float = 0,
    max_ascent: float = 99999,
    min_descent: float = 0,
    max_descent: float = 99999,
    min_speed_max: float = 0,
    max_speed_max: float = 9999,
    min_speed_avg: float = 0,
    max_speed_avg: float = 9999,
) -> pd.DataFrame:
    """Return a number of rows based on conditions.

    Args:
    ----
    filepath (str): Path where the extracted features are stored.
    random_size (int): Number of random data to return.
    random_state (int): Random state for reproducibility.
    activity_type (str): Activity type to return.
    min_total_distance (float): Minimum total distance in column to return.
    max_total_distance (float): Maximum total distance in column to return.
    min_duration (float): Minimum duration in column to return.
    max_duration (float): Maximum duration in column to return.
    min_calories (float): Minimum calories in column to return.
    max_calories (float): Maximum calories in column to return.
    min_hr_avg (float): Minimum average heart rate in column to return.
    max_hr_avg (float): Maximum average heart rate in column to return.
    min_hr_min (float): Minimum minimum heart rate in column to return.
    max_hr_min (float): Maximum minimum heart rate in column to return.
    min_hr_max (float): Minimum maximum heart rate in column to return.
    max_hr_max (float): Maximum maximum heart rate in column to return.
    min_altitude_avg (float): Minimum average altitude in column to return.
    max_altitude_avg (float): Maximum average altitude in column to return.
    min_altitude_min (float): Minimum minimum altitude in column to return.
    max_altitude_min (float): Maximum minimum altitude in column to return.
    min_altitude_max (float): Minimum maximum altitude in column to return.
    max_altitude_max (float): Maximum maximum altitude in column to return.
    min_ascent (float): Minimum ascent in column to return.
    max_ascent (float): Maximum ascent in column to return.
    min_descent (float): Minimum descent in column to return.
    max_descent (float): Maximum descent in column to return.
    min_speed_max (float): Minimum maximum speed in column to return.
    max_speed_max (float): Maximum maximum speed in column to return.
    min_speed_avg (float): Minimum average speed in column to return.
    max_speed_avg (float): Maximum average speed in column to return.

    Returns:
    -------
    pd.DataFrame: Random data from extracted features.
    """
    # Pandas read csv
    read_df_tcx_csv = pd.read_csv(
        filepath_or_buffer=filepath,
        sep=';',
        index_col='index',
    )

    filters = [
        read_df_tcx_csv['total_distance'].between(
            min_total_distance, max_total_distance,
        ),
        read_df_tcx_csv['duration'].between(min_duration, max_duration),
        read_df_tcx_csv['calories'].between(min_calories, max_calories),
        read_df_tcx_csv['hr_avg'].between(min_hr_avg, max_hr_avg),
        read_df_tcx_csv['hr_min'].between(min_hr_min, max_hr_min),
        read_df_tcx_csv['hr_max'].between(min_hr_max, max_hr_max),
        read_df_tcx_csv['altitude_avg'].between(
            min_altitude_avg, max_altitude_avg,
        ),
        read_df_tcx_csv['altitude_min'].between(
            min_altitude_min, max_altitude_min,
        ),
        read_df_tcx_csv['altitude_max'].between(
            min_altitude_max, max_altitude_max,
        ),
        read_df_tcx_csv['ascent'].between(min_ascent, max_ascent),
        read_df_tcx_csv['descent'].between(min_descent, max_descent),
        read_df_tcx_csv['speed_max'].between(min_speed_max, max_speed_max),
        read_df_tcx_csv['speed_avg'].between(min_speed_avg, max_speed_avg),
    ]

    # Check conditions
    if activity_type != 'any':
        filters.append(read_df_tcx_csv['activity_type'] == activity_type)

    for f in filters:
        read_df_tcx_csv = read_df_tcx_csv.loc[f]

    # Try to return condition based data
    try:
        return read_df_tcx_csv.sample(n=random_size, random_state=random_state)
    except ValueError:
        error_message = (
            f'Not enough data left to return {random_size} '
            f'random data. Ease the conditions.'
        )
        raise ValueError from ValueError(error_message)


def filter_returned_columns(
    columns_to_return: list,
    df_to_filter: pd.DataFrame,
) -> pd.DataFrame:
    """Filter returned columns and their order.

    Args:
    ----
    columns_to_return (list): Specific columns to return.
    df_to_filter (pd.DataFrame): Any dataframe.

    Returns:
    -------
    pd.DataFrame: Random data from extracted features.
    """
    all_possible_columns = df_to_filter.columns

    # Check if columns to return are in dataframe
    error_cols = list(set(columns_to_return) - set(all_possible_columns))
    if error_cols:
        # Raise error if columns are not in dataframe
        # and show possible columns
        error_message = (
            f'Columns {error_cols} not found in dataframe. '
            f'Possible columns are {all_possible_columns}.'
        )
        raise ValueError(error_message)

    return df_to_filter[columns_to_return]
