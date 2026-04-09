"""
Logger module.
Logs invalid files to a dated log file.
Fetches a GUID from external API for each log entry (Merit requirement).
"""

import os
import requests
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "logs")
GUID_API = "https://www.uuidtools.com/api/generate/v1"


def _get_guid() -> str:
    """Fetch a UUID v1 from external API. Falls back to 'N/A' if unavailable."""
    try:
        response = requests.get(GUID_API, timeout=5)
        response.raise_for_status()
        data = response.json()
        # API returns a list: ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"]
        return data[0] if isinstance(data, list) else str(data)
    except Exception:
        return "GUID-UNAVAILABLE"


def log_invalid_file(filename: str, reasons: list):
    """
    Write an error entry to today's log file.
    Each entry gets a unique GUID.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    log_path = os.path.join(LOG_DIR, f"error_log_{today}.txt")

    guid = _get_guid()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = (
        f"[{timestamp}]\n"
        f"  GUID     : {guid}\n"
        f"  File     : {filename}\n"
        f"  Reason(s): {'; '.join(reasons)}\n"
        f"{'-' * 60}\n"
    )

    with open(log_path, "a") as f:
        f.write(entry)

    return guid, log_path