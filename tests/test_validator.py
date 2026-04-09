"""
TDD Tests for the validator module.
Written BEFORE the implementation was finalised — following TDD principles.
"""

import os
import csv
import pytest
import tempfile

from src.validator import (
    CSVValidator,
    FilenameStrategy,
    ZeroByteStrategy,
    HeaderStrategy,
    DuplicateBatchIdStrategy,
    ReadingRangeStrategy,
    MissingColumnsStrategy,
)

VALID_HEADERS = [
    "batch_id", "timestamp",
    "reading1", "reading2", "reading3", "reading4", "reading5",
    "reading6", "reading7", "reading8", "reading9", "reading10"
]

def make_csv(filename, headers=None, rows=None, empty=False):
    """Helper: create a temp CSV file, return its path."""
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, filename)
    if empty:
        open(path, "w").close()
        return path
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        if headers is not None:
            writer.writerow(headers)
        if rows:
            writer.writerows(rows)
    return path


VALID_ROW = [55, "14:01:04", 9.875, 9.138, 1.115, 8.006, 3.84, 4.952, 9.038, 1.046, 2.179, 8.701]


# ── FilenameStrategy ──────────────────────────────────────────────────────────

class TestFilenameStrategy:
    s = FilenameStrategy()

    def test_valid_filename(self):
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, [VALID_ROW])
        ok, reason = self.s.validate(path)
        assert ok

    def test_invalid_filename_no_prefix(self):
        path = make_csv("data_20230603140104.csv", VALID_HEADERS, [VALID_ROW])
        ok, reason = self.s.validate(path)
        assert not ok
        assert "Invalid filename" in reason

    def test_invalid_filename_wrong_date_length(self):
        path = make_csv("MED_DATA_2023060314.csv", VALID_HEADERS, [VALID_ROW])
        ok, reason = self.s.validate(path)
        assert not ok

    def test_invalid_filename_not_csv(self):
        path = make_csv("MED_DATA_20230603140104.txt", VALID_HEADERS, [VALID_ROW])
        ok, reason = self.s.validate(path)
        assert not ok


# ── ZeroByteStrategy ──────────────────────────────────────────────────────────

class TestZeroByteStrategy:
    s = ZeroByteStrategy()

    def test_empty_file_fails(self):
        path = make_csv("MED_DATA_20230603140104.csv", empty=True)
        ok, reason = self.s.validate(path)
        assert not ok
        assert "0 bytes" in reason

    def test_non_empty_passes(self):
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, [VALID_ROW])
        ok, reason = self.s.validate(path)
        assert ok


# ── HeaderStrategy ────────────────────────────────────────────────────────────

class TestHeaderStrategy:
    s = HeaderStrategy()

    def test_correct_headers_pass(self):
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, [VALID_ROW])
        ok, reason = self.s.validate(path)
        assert ok

    def test_misspelled_batch_id_fails(self):
        bad = ["batch", "timestamp"] + [f"reading{i}" for i in range(1, 11)]
        path = make_csv("MED_DATA_20230603140104.csv", bad, [VALID_ROW])
        ok, reason = self.s.validate(path)
        assert not ok
        assert "batch_id" in reason

    def test_missing_reading_column_fails(self):
        bad = ["batch_id", "timestamp"] + [f"reading{i}" for i in range(1, 10)]  # only 9
        path = make_csv("MED_DATA_20230603140104.csv", bad)
        ok, reason = self.s.validate(path)
        assert not ok


# ── DuplicateBatchIdStrategy ──────────────────────────────────────────────────

class TestDuplicateBatchIdStrategy:
    s = DuplicateBatchIdStrategy()

    def test_unique_ids_pass(self):
        rows = [[i, "14:01:04"] + [1.0]*10 for i in range(1, 6)]
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, rows)
        ok, reason = self.s.validate(path)
        assert ok

    def test_duplicate_ids_fail(self):
        rows = [[55, "14:01:04"] + [1.0]*10 for _ in range(3)]
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, rows)
        ok, reason = self.s.validate(path)
        assert not ok
        assert "55" in reason


# ── ReadingRangeStrategy ──────────────────────────────────────────────────────

class TestReadingRangeStrategy:
    s = ReadingRangeStrategy()

    def test_valid_readings_pass(self):
        rows = [[i, "14:01:04"] + [1.5]*10 for i in range(1, 4)]
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, rows)
        ok, reason = self.s.validate(path)
        assert ok

    def test_reading_exactly_10_fails(self):
        rows = [[1, "14:01:04"] + [10.0] + [1.0]*9]
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, rows)
        ok, reason = self.s.validate(path)
        assert not ok

    def test_reading_9_9_passes(self):
        rows = [[1, "14:01:04"] + [9.9]*10]
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, rows)
        ok, reason = self.s.validate(path)
        assert ok

    def test_non_numeric_reading_fails(self):
        rows = [[1, "14:01:04"] + ["abc"] + [1.0]*9]
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, rows)
        ok, reason = self.s.validate(path)
        assert not ok


# ── Full CSVValidator ─────────────────────────────────────────────────────────

class TestCSVValidator:
    v = CSVValidator()

    def test_completely_valid_file(self):
        rows = [[i, "14:01:04"] + [1.5]*10 for i in range(1, 6)]
        path = make_csv("MED_DATA_20230603140104.csv", VALID_HEADERS, rows)
        ok, errors = self.v.validate(path)
        assert ok
        assert errors == []

    def test_invalid_filename_caught_first(self):
        rows = [[i, "14:01:04"] + [1.5]*10 for i in range(1, 3)]
        path = make_csv("WRONG_NAME.csv", VALID_HEADERS, rows)
        ok, errors = self.v.validate(path)
        assert not ok