"""TCX/GPX sportfile utilities."""

import os
from pathlib import Path


def find_small_files_and_delete(sportfile_directory: str) -> None:
    """Find uselessly small tcx/gpx files and delete them."""
    small_file_size = 2576
    for filename in os.listdir(sportfile_directory):
        file_size = os.path.getsize(sportfile_directory + filename)
        if file_size < small_file_size:
            # remove file
            Path.unlink(Path(sportfile_directory, filename))
