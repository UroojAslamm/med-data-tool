"""
CLI interface for the Medical Data Download Tool.
"""

import os
import sys
import tempfile
import argparse

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ftp_client import FTPClient
from src.validator import CSVValidator
from src.file_manager import store_valid_file
from src.logger import log_invalid_file
from src.tracker import DownloadTracker


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 2121
DEFAULT_USER = "ftpuser"
DEFAULT_PASS = "ftppass"


def run_pipeline(host, port, user, password, verbose=True):
    """Full download-validate-store pipeline. Returns summary dict."""
    tracker = DownloadTracker()
    validator = CSVValidator()
    summary = {"downloaded": 0, "valid": 0, "invalid": 0, "skipped": 0, "errors": []}

    def log(msg):
        if verbose:
            print(msg)

    log(f"\n{'='*55}")
    log(f"  Medical Data Download Tool")
    log(f"{'='*55}")
    log(f"  Connecting to FTP: {host}:{port}")

    client = FTPClient(host, port, user, password)
    try:
        client.connect()
        log("  Connected ✓")
    except Exception as e:
        log(f"  ERROR: Could not connect — {e}")
        summary["errors"].append(str(e))
        return summary

    with tempfile.TemporaryDirectory() as tmp:
        try:
            all_files = client.list_files()
        except Exception as e:
            log(f"  ERROR listing files: {e}")
            client.disconnect()
            return summary

        log(f"  Files on server: {len(all_files)}")

        new_files = [f for f in all_files if not tracker.has_seen(f)]
        log(f"  New (unseen) files: {len(new_files)}")
        summary["skipped"] = len(all_files) - len(new_files)

        for filename in new_files:
            log(f"\n  ▶ Processing: {filename}")
            try:
                local_path = client.download_file(filename, tmp)
                summary["downloaded"] += 1
            except Exception as e:
                log(f"    ✗ Download failed: {e}")
                summary["errors"].append(f"{filename}: {e}")
                continue

            is_valid, reasons = validator.validate(local_path)

            if is_valid:
                dest = store_valid_file(local_path)
                tracker.mark_seen(filename)
                log(f"    ✓ Valid — saved to: {dest}")
                summary["valid"] += 1
            else:
                guid, log_path = log_invalid_file(filename, reasons)
                tracker.mark_seen(filename)  # still mark seen — don't re-download
                log(f"    ✗ Invalid — {reasons[0]}")
                log(f"      GUID: {guid}")
                log(f"      Logged to: {log_path}")
                summary["invalid"] += 1

    client.disconnect()
    log(f"\n{'='*55}")
    log(f"  Done! Valid: {summary['valid']} | "
        f"Invalid: {summary['invalid']} | "
        f"Skipped (seen): {summary['skipped']}")
    log(f"{'='*55}\n")
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Medical Trial Data Download Tool — Centrala University"
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="FTP server host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="FTP server port")
    parser.add_argument("--user", default=DEFAULT_USER, help="FTP username")
    parser.add_argument("--password", default=DEFAULT_PASS, help="FTP password")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    run_pipeline(args.host, args.port, args.user, args.password, verbose=not args.quiet)


if __name__ == "__main__":
    main()