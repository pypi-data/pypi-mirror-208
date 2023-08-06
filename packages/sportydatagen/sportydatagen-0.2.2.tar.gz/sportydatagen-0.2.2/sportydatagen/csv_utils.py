"""Module for checking/deleting incomplete csv files."""

import os
from pathlib import Path

import pandas as pd
from sport_activities_features.tcx_manipulation import TCXFile

from sportydatagen.filetype import Filetype

# Class for reading TCX files
tcx_file = TCXFile()


def create_list_of_all_possible_files(number_of_files: int) -> list:
    """Create a list of all possible files.

    Args:
    ----
    number_of_files (int): Number of files.

    Returns:
    -------
    all_possible_csv_files (list): List of all possible files.
    """
    all_possible_csv_files = []
    for i in range(1, number_of_files + 1):
        all_possible_csv_files.append(f'{i}.csv')
    return all_possible_csv_files


def missing_csv_files(directory_path: str, number_of_files: int) -> list:
    """Find and print missing files.

    Prints missing files from all possible numbered
    sequence of tcx/gpx files converted to csv files. Csv files are stored in
    tcx_csv directory. The script will print a list of missing files.
    Files are missing if they have not been correctly converted to csv format.

    Args:
    ----
    directory_path (str): Path to directory with csv files.
    number_of_files (int): Number of files.

    Returns:
    -------
    str: List of missing files.
    """
    csv_files_in_directory = os.listdir(Path(directory_path))

    all_possible_files = create_list_of_all_possible_files(number_of_files)

    set_of_actual_csv_files = set(csv_files_in_directory)
    set_of_possible_csv_files = set(all_possible_files)

    return sorted(
        set_of_possible_csv_files - set_of_actual_csv_files,
    )


# iterate through files and print total distance of activities
def remove_empty_activities(all_files: list) -> None:
    """Remove tcx/gpx files that returns missing features."""
    for i in range(len(all_files)):
        activity = tcx_file.read_one_file(all_files[i])
        temp = activity['total_distance'] / 1000
        if temp == 0:
            print(f'Empty activity in file: {all_files[i]}')
            Path.unlink(Path(all_files[i]))


def delete_empty_csv_files(csv_directory: str) -> None:
    """Delete empty csv files in directory."""
    basically_empty = 110

    for file in os.listdir(csv_directory):
        temp_file_size = os.path.getsize(csv_directory + file)

        if temp_file_size <= basically_empty:
            print(f'Empty csv file: {file} in {csv_directory} directory')
            Path.unlink(Path(csv_directory, file))


# Function to check if heartrate exists
def check_file_delete_csv_if_columns_are_nan(
    csv_directory: str,
    columns_to_check: list = None,
) -> None:
    """Check if columns are nan in df and delete corresponding csv file.

    Args:
    ----
    csv_directory (str): Path to csv directory.
    columns_to_check (list): List of columns to check.

    Returns:
    -------
    None
    """
    if columns_to_check is None:
        columns_to_check = [
            'heartrates',
            'latitude',
            'longitude',
            'altitudes',
            'distances',
            'total_distance',
            'timestamps',
            'heartrates',
            'speeds',
        ]
    for filename in os.listdir(csv_directory):
        file_to_csv_df = pd.read_csv(csv_directory + filename, sep=';')

        if file_to_csv_df[columns_to_check].isna().to_numpy().any():
            print(f'Something is empty in {csv_directory}{filename}')
            Path.unlink(Path(csv_directory, filename))


# Function to compare tcx and csv files if both exist
def delete_unmatching_sportfiles_and_csvs(
    sportfile_directory: str,
    csv_directory: str,
    filetype: Filetype,
) -> None:
    """Delete sport files that are not in csv and vice versa."""
    csv_file_extension = '.csv'
    file_extension = ''
    if filetype == Filetype.TCX:
        file_extension = '.tcx'
    elif filetype == Filetype.GPX:
        file_extension = '.gpx'
    elif filetype == Filetype.UNKNOWN:
        error_message = 'Filetype unknown'
        raise ValueError(error_message)

    # Get all files in sport file directory
    sport_files_in_directory = os.listdir(Path(Path.cwd(), file_extension[1:]))
    # Get all files in csv directory
    csv_files_in_directory = os.listdir(Path(Path.cwd(), csv_directory))
    # Remove .tcx/.gpx and .csv from filenames
    sport_files_in_directory = [
        i.replace(file_extension, '') for i in sport_files_in_directory
    ]
    csv_files_in_directory = [
        i.replace(csv_file_extension, '') for i in csv_files_in_directory
    ]
    # Get difference between sport and csv files
    set_tcx_not_in_csv = set(sport_files_in_directory) - set(
        csv_files_in_directory,
    )
    set_csv_not_in_tcx = set(csv_files_in_directory) - set(
        sport_files_in_directory,
    )

    # Delete tcx/gpx files that are not in csv
    # i.e. 35.tcx is to be deleted, 35.csv does not exist
    for value in set_tcx_not_in_csv:
        print('Deleting ' + sportfile_directory + value + file_extension)
        Path.unlink(Path(sportfile_directory + value + file_extension))

    # Delete csv files that are not in tcx
    for value in set_csv_not_in_tcx:
        print('Deleting ' + csv_directory + value + csv_file_extension)
        Path.unlink(Path(csv_directory + value + csv_file_extension))
