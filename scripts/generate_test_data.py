"""
Automation script to generate valid and invalid CSV test files.
Covers Task 2 - automation techniques.
"""

import csv
import os
import random
import string
from datetime import datetime, timedelta


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "ftp_server", "ftp_files")


def random_timestamp():
    base = datetime(2023, 6, 1, 8, 0, 0)
    offset = timedelta(seconds=random.randint(0, 86400))
    return (base + offset).strftime("%H:%M:%S")


def random_reading(invalid=False):
    if invalid:
        return round(random.uniform(10.0, 20.0), 3)  # exceeds 9.9 — INVALID
    return round(random.uniform(0.1, 9.9), 3)


def make_filename(dt=None):
    if dt is None:
        dt = datetime.now()
    return f"MED_DATA_{dt.strftime('%Y%m%d%H%M%S')}.csv"


def write_valid_file(path, num_rows=10):
    """Generate a perfectly valid CSV file."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "batch_id", "timestamp",
            "reading1", "reading2", "reading3", "reading4", "reading5",
            "reading6", "reading7", "reading8", "reading9", "reading10"
        ])
        used_ids = set()
        for _ in range(num_rows):
            bid = random.randint(10, 999)
            while bid in used_ids:
                bid = random.randint(10, 999)
            used_ids.add(bid)
            row = [bid, random_timestamp()] + [random_reading() for _ in range(10)]
            writer.writerow(row)
    print(f"  [VALID]   {os.path.basename(path)}")


def write_invalid_filename_file(path):
    """Bad filename — not matching MED_DATA_YYYYMMDDHHMMSS.csv"""
    # We write it but name it wrong
    bad_path = os.path.join(os.path.dirname(path), "bad_name_file.csv")
    write_valid_file(bad_path)
    print(f"  [INVALID - bad filename] {os.path.basename(bad_path)}")


def write_duplicate_batch_id_file(path):
    """File with duplicate batch_ids."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "batch_id", "timestamp",
            "reading1", "reading2", "reading3", "reading4", "reading5",
            "reading6", "reading7", "reading8", "reading9", "reading10"
        ])
        for _ in range(5):
            row = [55, random_timestamp()] + [random_reading() for _ in range(10)]
            writer.writerow(row)
    print(f"  [INVALID - dup batch_id] {os.path.basename(path)}")


def write_wrong_header_file(path):
    """File with misspelled header."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        # "batch" instead of "batch_id"
        writer.writerow([
            "batch", "timestamp",
            "reading1", "reading2", "reading3", "reading4", "reading5",
            "reading6", "reading7", "reading8", "reading9", "reading10"
        ])
        for _ in range(5):
            row = [random.randint(10, 999), random_timestamp()] + [random_reading() for _ in range(10)]
            writer.writerow(row)
    print(f"  [INVALID - bad header]   {os.path.basename(path)}")


def write_invalid_reading_file(path):
    """File with a reading value of 10 or greater."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "batch_id", "timestamp",
            "reading1", "reading2", "reading3", "reading4", "reading5",
            "reading6", "reading7", "reading8", "reading9", "reading10"
        ])
        for i in range(5):
            readings = [random_reading() for _ in range(9)] + [random_reading(invalid=True)]
            row = [random.randint(10, 999), random_timestamp()] + readings
            writer.writerow(row)
    print(f"  [INVALID - bad reading]  {os.path.basename(path)}")


def write_zero_byte_file(path):
    """Empty 0-byte file."""
    open(path, "w").close()
    print(f"  [INVALID - 0 byte]       {os.path.basename(path)}")


def write_missing_columns_file(path):
    """File missing some reading columns."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "timestamp", "reading1", "reading2"])
        for _ in range(5):
            row = [random.randint(10, 999), random_timestamp(), random_reading(), random_reading()]
            writer.writerow(row)
    print(f"  [INVALID - missing cols] {os.path.basename(path)}")


def generate_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nGenerating test files into: {OUTPUT_DIR}\n")

    now = datetime.now()

    # 3 valid files
    for i in range(3):
        dt = now + timedelta(seconds=i * 5)
        write_valid_file(os.path.join(OUTPUT_DIR, make_filename(dt)))

    # Invalid files
    dt = now + timedelta(seconds=20)
    write_duplicate_batch_id_file(os.path.join(OUTPUT_DIR, make_filename(dt)))

    dt = now + timedelta(seconds=25)
    write_wrong_header_file(os.path.join(OUTPUT_DIR, make_filename(dt)))

    dt = now + timedelta(seconds=30)
    write_invalid_reading_file(os.path.join(OUTPUT_DIR, make_filename(dt)))

    dt = now + timedelta(seconds=35)
    write_zero_byte_file(os.path.join(OUTPUT_DIR, make_filename(dt)))

    dt = now + timedelta(seconds=40)
    write_missing_columns_file(os.path.join(OUTPUT_DIR, make_filename(dt)))

    write_invalid_filename_file(os.path.join(OUTPUT_DIR, make_filename(now)))

    print(f"\nDone! {len(os.listdir(OUTPUT_DIR))} files in FTP folder.")


if __name__ == "__main__":
    generate_all()