"""
Tracks which files have already been downloaded.
Prevents downloading the same file twice (no duplicate datasets).
Uses a simple JSON file as persistent storage.
"""

import json
import os


TRACKER_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "downloaded.json")


class DownloadTracker:

    def __init__(self, tracker_path: str = TRACKER_FILE):
        self.tracker_path = os.path.abspath(tracker_path)
        self._seen: set = self._load()

    def _load(self) -> set:
        if os.path.exists(self.tracker_path):
            with open(self.tracker_path) as f:
                return set(json.load(f))
        return set()

    def _save(self):
        os.makedirs(os.path.dirname(self.tracker_path), exist_ok=True)
        with open(self.tracker_path, "w") as f:
            json.dump(sorted(self._seen), f, indent=2)

    def has_seen(self, filename: str) -> bool:
        return filename in self._seen

    def mark_seen(self, filename: str):
        self._seen.add(filename)
        self._save()

    def all_seen(self) -> list:
        return sorted(self._seen)