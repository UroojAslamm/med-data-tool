"""
Manages storing valid CSV files in a date/time-based directory hierarchy.
Structure: data/valid/YYYY/MM/DD/filename.csv
"""

import os
import re
import shutil
from datetime import datetime


VALID_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "valid")
FILENAME_PATTERN = re.compile(r"MED_DATA_(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})\.csv")


def store_valid_file(filepath: str) -> str:
    """
    Copy a valid file into the archive structure.
    Returns the destination path.
    """
    filename = os.path.basename(filepath)
    match = FILENAME_PATTERN.match(filename)

    if match:
        year, month, day = match.group(1), match.group(2), match.group(3)
    else:
        # Fallback to today's date
        now = datetime.now()
        year, month, day = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")

    dest_dir = os.path.join(VALID_DIR, year, month, day)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(filepath, dest_path)
    return dest_path