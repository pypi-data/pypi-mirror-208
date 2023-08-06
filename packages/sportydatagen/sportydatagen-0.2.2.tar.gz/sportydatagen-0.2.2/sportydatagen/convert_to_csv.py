"""Convert GPX file to CSV file."""
import contextlib
import os
from pathlib import Path

import pandas as pd
from sport_activities_features import TCXFile
from sport_activities_features.gpx_manipulation import GPXFile

from sportydatagen.csv_utils import (
    check_file_delete_csv_if_columns_are_nan,
    delete_empty_csv_files,
)


# Function to merge CSV files
def merge_csv_files(
    input_files: list,
    output_file: str,
) -> None:
    """Merge CSV files with same columns."""
    # Path to output file
    output_file = str(Path(output_file))

    # List of DataFrames
    dataframes = []

    # Iterate through files
    for input_file in input_files:
        # Read CSV file
        dataframe = pd.read_csv(input_file, sep=';')
        # Add extracted feature file name to DataFrame
        dataframe['merged_from'] = Path(input_file).name
        # Append DataFrame to list
        dataframes.append(dataframe)

    # Merge all DataFrames
    merged_dataframe = pd.concat(dataframes, axis=0)

    if 'index' in merged_dataframe.columns:
        # Delete column index
        del merged_dataframe['index']
    if 'row_id' in merged_dataframe.columns:
        # Delete column row_id
        del merged_dataframe['row_id']
    # Create column index
    merged_dataframe['index'] = range(1, len(merged_dataframe) + 1)

    # Shift last column to first position in dataframe
    cols = list(merged_dataframe.columns)
    cols = [cols[-1]] + cols[:-1]
    merged_dataframe = merged_dataframe[cols]

    # Write merged DataFrame to CSV file
    merged_dataframe.to_csv(output_file, index=False, sep=';')


def check_missing_only_heartrates(
    df: pd.DataFrame,
    percent_miss_hr_allowed: int = 3,
) -> bool:
    """Check if only heartrates are missing and in less than 3%."""
    # Get percentage of missing values for each column
    percent_missing_values = 100 * df.isna().sum() / len(df)
    # Create table with results
    missing_values_df = pd.concat([percent_missing_values], axis=1)
    # Rename column
    mis_val_table_ren_columns = missing_values_df.rename(
        columns={0: '% of missing total values'},
    )
    # Sort table by percentage of missing values
    # Only keep columns with missing values
    mis_val_table_ren_columns = (
        mis_val_table_ren_columns[mis_val_table_ren_columns.iloc[:, 0] != 0]
        .sort_values('% of missing total values', ascending=False)
        .round(1)
    )
    # If only one column is missing
    return (
        len(mis_val_table_ren_columns) == 1
        and (
            # And that column is heartrates
            mis_val_table_ren_columns.index[0]
            == 'heartrates'
        )
        and (
            # And that column has less than 2% of missing values
            mis_val_table_ren_columns['% of missing total values'][0]
            < percent_miss_hr_allowed
        )
    )


def fill_empty_heartrates(heartrates: pd.Series) -> pd.Series:
    """Fill empty heartrates with linear interpolation."""
    try:
        heartrates = heartrates.interpolate(
            method='linear', limit=45, limit_direction='both',
        )
        if str(heartrates[0]) == 'nan':
            heartrates[0] = heartrates[1]
        if str(heartrates[len(heartrates) - 1]) == 'nan':
            heartrates[len(heartrates) - 1] = heartrates[len(heartrates) - 2]
    except ValueError:
        # Too many consecutive NaN values
        return heartrates
    return heartrates


def check_file_type(
    input_file: str,
) -> TCXFile | GPXFile | None:
    """Check file type and return corresponding class."""
    if input_file.endswith('.tcx'):
        # Class for reading TCX files
        return TCXFile()
    if input_file.endswith('.gpx'):
        # Class for reading GPX files
        return GPXFile()
    return None


def convert_single_file(
    input_file: str,
    output_dir: str,
) -> pd.DataFrame | None:
    """Read and convert TCX/GPX file to CSV file."""
    sport_file = check_file_type(input_file)

    data = sport_file.read_one_file(input_file)
    if data is None:
        print('File format not supported: ' + input_file)
        return None

    # Path to newly created output CSV file
    output_file = Path(output_dir + Path(input_file).stem + '.csv')
    # Print progress
    print('Converting file: ' + str(output_file))
    # Convert dictionary of lists to pandas DataFrame
    df_to_csv = pd.DataFrame.from_dict(data)

    try:
        # Extract latitude and longitude from positions
        df_to_csv[['latitude', 'longitude']] = pd.DataFrame(
            df_to_csv['positions'].tolist(),
        )
        # Drop positions column
        df_to_csv = df_to_csv.drop(['positions'], axis=1)
        # Reorder columns
        df_to_csv = df_to_csv[
            [
                'activity_type',
                'latitude',
                'longitude',
                'altitudes',
                'distances',
                'total_distance',
                'timestamps',
                'heartrates',
                'speeds',
            ]
        ]

        # Set index name
        df_to_csv.index.name = 'row_id'

        # Round DataFrame to 2 decimals
        df_to_csv = df_to_csv.round(
            {'altitudes': 2, 'distances': 2, 'speeds': 2},
        )
        # Check if DataFrame contains NaN values
        # and if only heartrates are missing
        if df_to_csv.isna().to_numpy().any() and check_missing_only_heartrates(
            df_to_csv,
        ):
            # Interpolate missing heartrates
            df_to_csv['heartrates'] = fill_empty_heartrates(
                df_to_csv['heartrates'],
            )
        # Some GPX files are missing heartrates
        try:
            # Remove decimals from heartrates
            df_to_csv['heartrates'] = df_to_csv.heartrates.apply(int)
        except TypeError:
            contextlib.suppress(TypeError)
        # Save DataFrame to CSV file with semicolon as separator
        df_to_csv.to_csv(output_file, header=True, sep=';')
    except ValueError:
        print('Error reading file: ' + input_file)
        pass
    return df_to_csv


def convert_directory_of_files_to_csv(
    input_sportfile_directory: str,
    output_csv_dir: str,
) -> None:
    """Read and convert all TCX/GPX files in directory to CSV files."""
    for filename in os.listdir(input_sportfile_directory):
        # Path to input TCX/GPX file
        input_file = str(Path(input_sportfile_directory, filename))
        # Path to newly created output CSV file
        convert_single_file(input_file, output_csv_dir)


def convert_sportfiles_and_remove_empty_csvs(
    input_sportfile_directory: str,
    output_csv_dir: str,
) -> None:
    """Read, convert and remove empty csv files."""
    # Read and convert TCX files to CSV files
    convert_directory_of_files_to_csv(
        input_sportfile_directory=input_sportfile_directory,
        output_csv_dir=output_csv_dir,
    )
    # Remove empty CSV files
    delete_empty_csv_files(csv_directory=output_csv_dir)
    # Remove CSV files with NaN values
    check_file_delete_csv_if_columns_are_nan(
        csv_directory=output_csv_dir,
        columns_to_check=None,  # If None, all columns are checked
    )
