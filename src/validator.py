"""
Validator module using the Strategy design pattern.
Each validation rule is a separate strategy class.
This makes it easy to add/remove/reorder checks without touching other code.
"""

import csv
import os
import re
from abc import ABC, abstractmethod
from typing import Tuple


# ── Base Strategy ────────────────────────────────────────────────────────────

class ValidationStrategy(ABC):
    """Abstract base class for all validation strategies."""

    @abstractmethod
    def validate(self, filepath: str) -> Tuple[bool, str]:
        """
        Returns (True, "") if valid, or (False, "reason") if invalid.
        """
        pass


# ── Concrete Strategies ───────────────────────────────────────────────────────

class FilenameStrategy(ValidationStrategy):
    """Check filename matches MED_DATA_YYYYMMDDHHMMSS.csv"""
    PATTERN = re.compile(r"^MED_DATA_\d{14}\.csv$")

    def validate(self, filepath: str) -> Tuple[bool, str]:
        name = os.path.basename(filepath)
        if not self.PATTERN.match(name):
            return False, f"Invalid filename format: '{name}'"
        return True, ""


class ZeroByteStrategy(ValidationStrategy):
    """Reject empty files."""

    def validate(self, filepath: str) -> Tuple[bool, str]:
        if os.path.getsize(filepath) == 0:
            return False, "File is 0 bytes (empty)"
        return True, ""


class HeaderStrategy(ValidationStrategy):
    """Check that required headers are present and correctly spelled."""
    REQUIRED = [
        "batch_id", "timestamp",
        "reading1", "reading2", "reading3", "reading4", "reading5",
        "reading6", "reading7", "reading8", "reading9", "reading10"
    ]

    def validate(self, filepath: str) -> Tuple[bool, str]:
        try:
            with open(filepath, newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
        except Exception as e:
            return False, f"Could not read file: {e}"

        if headers is None:
            return False, "File has no headers"

        # Strip whitespace from headers
        headers = [h.strip() for h in headers]

        missing = [h for h in self.REQUIRED if h not in headers]
        if missing:
            return False, f"Missing or misspelled headers: {missing}"
        return True, ""


class DuplicateBatchIdStrategy(ValidationStrategy):
    """Reject files that have duplicate batch_ids within the same file."""

    def validate(self, filepath: str) -> Tuple[bool, str]:
        try:
            with open(filepath, newline="") as f:
                reader = csv.DictReader(f)
                seen = set()
                duplicates = set()
                for row in reader:
                    bid = row.get("batch_id", "").strip()
                    if bid in seen:
                        duplicates.add(bid)
                    seen.add(bid)
        except Exception as e:
            return False, f"Could not parse file: {e}"

        if duplicates:
            return False, f"Duplicate batch_ids found: {sorted(duplicates)}"
        return True, ""


class ReadingRangeStrategy(ValidationStrategy):
    """All 10 readings must be floats in range 0.0 to 9.9 (inclusive)."""
    READING_COLS = [f"reading{i}" for i in range(1, 11)]

    def validate(self, filepath: str) -> Tuple[bool, str]:
        try:
            with open(filepath, newline="") as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    for col in self.READING_COLS:
                        val = row.get(col, "").strip()
                        try:
                            num = float(val)
                        except ValueError:
                            return False, f"Row {row_num}, {col}: not a number ('{val}')"
                        if num >= 10.0 or num < 0:
                            return False, f"Row {row_num}, {col}: value {num} out of range (must be 0–9.9)"
        except Exception as e:
            return False, f"Could not parse file: {e}"
        return True, ""


class MissingColumnsStrategy(ValidationStrategy):
    """Every row must have all 12 columns (no missing cells)."""

    def validate(self, filepath: str) -> Tuple[bool, str]:
        try:
            with open(filepath, newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                expected_count = len(headers)
                for row_num, row in enumerate(reader, start=2):
                    if len(row) != expected_count:
                        return False, (
                            f"Row {row_num} has {len(row)} columns, "
                            f"expected {expected_count}"
                        )
        except Exception as e:
            return False, f"Could not parse file: {e}"
        return True, ""


# ── Validator (Context) ───────────────────────────────────────────────────────

class CSVValidator:
    """
    Context class that runs all validation strategies in order.
    This is the Strategy Pattern's 'Context'.
    """

    def __init__(self):
        self._strategies = [
            FilenameStrategy(),
            ZeroByteStrategy(),
            HeaderStrategy(),
            MissingColumnsStrategy(),
            DuplicateBatchIdStrategy(),
            ReadingRangeStrategy(),
        ]

    def validate(self, filepath: str) -> Tuple[bool, list]:
        """
        Run all strategies. Returns (is_valid, list_of_errors).
        Stops at first failure for efficiency.
        """
        for strategy in self._strategies:
            passed, reason = strategy.validate(filepath)
            if not passed:
                return False, [reason]
        return True, []