"""Feature extraction utils, used by both gpx and tcx feature extraction.

Manually extracting data from TCX and GPX files.
"""

import datetime as dt
import os
from pathlib import Path

import pandas as pd
from sport_activities_features import (
    BanisterTRIMPv1,
    BanisterTRIMPv2,
    EdwardsTRIMP,
    GPXFile,
    LuciaTRIMP,
    TCXFile,
)

from sportydatagen.filetype import Filetype


def calculate_duration(read_df_tcx_csv: pd.DataFrame) -> int:
    """Calculate duration of activity in seconds.

    Args:
    ----
    read_df_tcx_csv (pd.DataFrame): Dataframe with timestamps.

    Returns:
    -------
    total_seconds (int): Duration of activity in seconds.
    """
    try:
        start_time = dt.datetime.strptime(
            read_df_tcx_csv['timestamps'][0],
            '%Y-%m-%d %H:%M:%S',
        ).astimezone()
        end_time = dt.datetime.strptime(
            read_df_tcx_csv['timestamps'][len(read_df_tcx_csv) - 1],
            '%Y-%m-%d %H:%M:%S',
        ).astimezone()
    except ValueError:
        try:
            """
            This is a try-except block.
            Timestamp is expected to be in ISO 8601 format.
            This is a simple naive fix for the files.
            """
            start_time = dt.datetime.strptime(
                read_df_tcx_csv['timestamps'][0],
                '%Y-%m-%d %H:%M:%S%z',
            ).astimezone()
            end_time = dt.datetime.strptime(
                read_df_tcx_csv['timestamps'][len(read_df_tcx_csv) - 1],
                '%Y-%m-%d %H:%M:%S%z',
            ).astimezone()
        except ValueError:
            error_message = (
                'Timestamps in dataframe are not in ISO 8601 format'
            )
            raise ValueError from ValueError(error_message)
    except KeyError:
        error_message = 'No column timestamp in dataframe'
        raise KeyError from KeyError(error_message)

    return int((end_time - start_time).total_seconds())


def calculate_ascent_descent(read_df_tcx_csv: pd.DataFrame) -> tuple:
    """Calculate ascent and descent of activity in meters."""
    try:
        diff = read_df_tcx_csv['altitudes'].diff()
    except KeyError:
        return 0, 0

    # Create new columns 'ascent' and 'descent'
    # Calculate ascent
    read_df_tcx_csv['ascent'] = diff.where(diff > 0, 0)
    # Sum of dataframe column ascent
    full_ascent = read_df_tcx_csv['ascent'].sum()

    # Calculate descent
    read_df_tcx_csv['descent'] = (-diff).where(diff < 0, 0)
    # Sum of dataframe column descent
    full_descent = read_df_tcx_csv['descent'].sum()
    return full_ascent, full_descent


def extract_features(
    read_df_csv: pd.DataFrame,
    sport_file: GPXFile() or TCXFile() or None = None,
    sportfile_directory: str | None = None,
    original_filename: str | None = None,
    index: int = 1,
) -> dict:
    """Extract features from a single TCX/GPX file."""
    calories = 'NULL'
    lucia_trimp = 'NULL'
    edwards_trimp = 'NULL'

    # Extract metrics manually from dataframe
    activity_type = read_df_csv['activity_type'][0]
    total_distance = read_df_csv['total_distance'][len(read_df_csv) - 1]
    hr_avg = read_df_csv['heartrates'].mean()
    hr_max = read_df_csv['heartrates'].max()
    hr_min = read_df_csv['heartrates'].min()
    altitude_avg = read_df_csv['altitudes'].mean()
    altitude_max = read_df_csv['altitudes'].max()
    altitude_min = read_df_csv['altitudes'].min()
    duration = calculate_duration(read_df_csv)
    ascent, descent = calculate_ascent_descent(read_df_csv)
    # speed_min has been removed since it is always 0
    speed_max = read_df_csv['speeds'].max()
    speed_avg = read_df_csv['speeds'].mean()

    # Banister's simple TRIMP
    banister = BanisterTRIMPv1(duration, hr_avg)
    banister_trimp_v1 = banister.calculate_TRIMP()

    # Banister's TRIMP V2
    banister_v2 = BanisterTRIMPv2(duration, hr_avg, hr_min, hr_max)

    banister_trimp_v2 = banister_v2.calculate_TRIMP()

    # If sport_file is not None and path to original file is known,
    # extract calories, else set calories to 'NULL'
    if sport_file is not None and sportfile_directory is not None:
        if original_filename is None:
            original_filename = 'NULL'
            relative_path_of_original_file = None
        else:
            # Check if original file exists
            relative_path_of_original_file = Path(
                sportfile_directory, original_filename,
            )
        if relative_path_of_original_file is not None and Path.exists(
            Path(sportfile_directory, original_filename),
        ):
            # Extract Integral Metrics using sports_activities_features
            activity_metrics = sport_file.extract_integral_metrics(
                str(relative_path_of_original_file),
            )
            # Extract calories from dictionary
            calories = activity_metrics['calories']
            activity = sport_file.read_one_file(relative_path_of_original_file)
            timestamps = activity['timestamps']
            heart_rates = activity['heartrates']

            edwards = EdwardsTRIMP(
                heart_rates, timestamps, max_heart_rate=hr_max,
            )
            edwards_trimp = edwards.calculate_TRIMP()

            lucia = LuciaTRIMP(heart_rates, timestamps, VT1=160, VT2=180)
            lucia_trimp = lucia.calculate_TRIMP()

    # Calories are not available in TCX files
    # they are calculated in sport_activities_features
    return {
        'index': index,
        'activity_type': activity_type,
        'total_distance': round(total_distance, 2),
        'duration': duration,
        'calories': calories,
        'hr_avg': round(hr_avg),
        'hr_min': hr_min,
        'hr_max': hr_max,
        'altitude_avg': round(altitude_avg, 2),
        'altitude_min': altitude_min,
        'altitude_max': altitude_max,
        'ascent': ascent,
        'descent': descent,
        'speed_max': speed_max,
        'speed_avg': speed_avg,
        'banister_simple_TRIMP': banister_trimp_v1,
        'banister_TRIMP': banister_trimp_v2,
        'edwards_TRIMP': edwards_trimp,
        'lucia_TRIMP': lucia_trimp,
        'file_name': original_filename,
    }


def extract_single_sportfile_metrics_to_csv(
    read_df_csv: pd.DataFrame,
    sportfile_directory: str | None = None,
    original_filename: str | None = None,
    index: int = 1,
) -> dict | None:
    """Metric extraction from sports file using saf.

    Extract metrics from single TCX/GPX file using sports_activities_features.
    """
    sport_file = None

    if original_filename is not None:
        if original_filename.endswith('.gpx'):
            sport_file = GPXFile()
        elif original_filename.endswith('.tcx'):
            sport_file = TCXFile()

    # Extract Integral Metrics using sports_activities_features
    return extract_features(
        read_df_csv=read_df_csv,
        sport_file=sport_file,
        sportfile_directory=sportfile_directory,
        original_filename=original_filename,
        index=index,
    )


def extract_features_csv_files_directory_to_csv(
    input_csv_directory: str,
    output_file: str,
    filetype: Filetype = Filetype.UNKNOWN,
    sportfile_directory: str | None = None,
) -> None:
    """Extract data from csvs converted from TCX/GPX files using pandas."""
    # Counter for index
    i = 1
    # Create a new dataframe for the extracted metrics
    df_to_save_to = pd.DataFrame()

    for filename in os.listdir(input_csv_directory):
        # Print progress
        print(
            f'Progress: {i}/{len(os.listdir(input_csv_directory))},'
            f' Extracting from: {filename}',
        )

        # Pandas read csv
        read_df_csv = pd.read_csv(input_csv_directory + filename, sep=';')
        # Set original filename
        original_filename = None
        # If filetype is not unknown, set original filename
        if filetype is not filetype.UNKNOWN:
            if filetype == filetype.GPX:
                original_filename = filename.replace('.csv', '.gpx')
            elif filetype == filetype.TCX:
                original_filename = filename.replace('.csv', '.tcx')

        # Extract data from a single GPX/TCX file, add filename and index
        row_to_append = extract_single_sportfile_metrics_to_csv(
            read_df_csv=read_df_csv,
            sportfile_directory=sportfile_directory,
            original_filename=original_filename,
            index=i,
        )

        # Pandas concat dictionary to empty dataframe
        row_to_append = pd.DataFrame([row_to_append]).round(2)
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
