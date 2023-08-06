"""Utility functions for sportydatagen."""

import csv
from pathlib import Path

from sportydatagen.activity import Activity


# duration,distance,calories,activity_type
def read_basic_dataset(filename: str) -> list:
    """Read basic dataset from a csv file."""
    dataset = []
    with Path.open(Path(filename)) as file:
        # Check if file has header.
        has_header = csv.Sniffer().has_header(file.read(1024))
        reader = csv.reader(file, delimiter=',')
        # Reset file pointer to beginning.
        file.seek(0)
        if has_header:
            # Skip header row.
            next(reader)
        for activity in reader:
            dataset.append(
                Activity(
                    activity[4],
                    float(activity[2]),
                    float(activity[1]),
                    float(activity[3]),
                ),
            )
        return dataset


def read_dataset(filename: str) -> list:
    """Read full dataset from a csv file."""
    dataset = []
    with Path.open(Path(filename)) as file:
        # Check if file has header.
        has_header = csv.Sniffer().has_header(file.read(4096))
        reader = csv.reader(file, delimiter=';')
        # Reset file pointer to beginning.
        file.seek(0)
        if has_header:
            # Skip header row.
            next(reader)
        for activity in reader:
            dataset.append(
                Activity(
                    activity_type=activity[1],  # string
                    distance=float(activity[2]),  # float
                    duration=float(activity[3]),  # float
                    calories=float(activity[4]),  # float
                    hr_avg=float(activity[5]),  # float
                    hr_min=float(activity[6]),  # float
                    hr_max=float(activity[7]),  # float
                    altitude_avg=float(activity[8]),  # float
                    altitude_min=float(activity[9]),  # float
                    altitude_max=float(activity[10]),  # float
                    ascent=float(activity[11]),  # float
                    descent=float(activity[12]),  # float
                    speed_max=float(activity[13]),  # float
                    speed_avg=float(activity[14]),  # float
                    file_name=activity[15],
                ),
            )  # string
        return dataset
