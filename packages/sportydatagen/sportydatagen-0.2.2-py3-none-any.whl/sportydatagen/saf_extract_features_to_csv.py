"""Extracting data from multiple TCX files using sport-activities-features."""

import os
from pathlib import Path

import pandas as pd
from sport_activities_features import GPXFile, TCXFile

from sportydatagen.convert_to_csv import check_file_type


def saf_extract_metrics_convert_to_csv(
    sportfile_directory: str,
    output_file: str,
) -> None:
    """Convert TCX/GPX files to CSV file using sports-activities-features."""
    # Create a new dataframe for the extracted metrics
    df_to_save_to = pd.DataFrame(
        columns=[
            'index',
            'filename',
            'activity_type',
            'distance',
            'duration',
            'calories',
            'hr_avg',
            'hr_max',
            'hr_min',
            'altitude_avg',
            'altitude_max',
            'altitude_min',
            'ascent',
            'descent',
            'steps',
        ],
        index=[0],
    )
    # Set filename as index
    df_to_save_to = df_to_save_to.set_index('filename')
    # Counter for index
    i = 1
    # Remove first row beacuse it is empty
    df_to_save_to = df_to_save_to.drop(df_to_save_to.index[0])

    # Extract data from a single TCX file using sports_activities_features
    TCXFile()
    GPXFile()

    for filename in os.listdir(sportfile_directory):
        """Extract metrics from sportfile file using sports_activities_features
        :return: pd.DataFrame with metrics"""

        # Print progress
        print(filename)

        sport_file = check_file_type(filename)

        if sport_file is None:
            print(f'File {filename} is not TCX or GPX file')
            return

        activity_metrics = sport_file.extract_integral_metrics(
            sportfile_directory + filename,
        )

        # Add index to dictionary
        activity_metrics['index'] = i
        # Add filename to dictionary
        activity_metrics['filename'] = filename

        # Pandas concat dictionary to empty dataframe
        row_to_append = pd.DataFrame([activity_metrics]).round(2)
        # Concat rows to dataframe
        df_to_save_to = pd.concat([df_to_save_to, row_to_append])
        # Increment index
        i += 1

    # Save to csv
    df_to_save_to.to_csv(
        Path(output_file),
        sep=';',
        na_rep='NULL',
        index=False,
    )
    # Drop rows with any null values, ignore activity_type column
    df_to_save_to = df_to_save_to.dropna(
        subset=df_to_save_to.columns.difference(['activity_type', 'steps']),
        how='any',
        axis=0,
    )
    # Replace output file with no null values
    output_file = output_file.replace('.csv', '_no_null.csv')
    # Save new csv with no null values
    df_to_save_to.to_csv(
        Path(output_file),
        sep=';',
        na_rep='NULL',
        index=False,
    )
