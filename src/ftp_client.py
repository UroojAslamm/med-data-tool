"""
FTP client module.
Connects to FTP server, lists files, downloads unseen files to a temp folder.
"""

import ftplib
import os
import tempfile
from typing import List


class FTPClient:

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._ftp = None

    def connect(self):
        self._ftp = ftplib.FTP()
        self._ftp.connect(self.host, self.port, timeout=10)
        self._ftp.login(self.username, self.password)

    def disconnect(self):
        if self._ftp:
            try:
                self._ftp.quit()
            except Exception:
                pass
            self._ftp = None

    def list_files(self) -> List[str]:
        """Return list of filenames on the FTP server."""
        if not self._ftp:
            raise RuntimeError("Not connected to FTP server.")
        files = []
        self._ftp.retrlines("NLST", files.append)
        return files

    def download_file(self, filename: str, dest_folder: str) -> str:
        """
        Download a single file to dest_folder.
        Returns local filepath.
        """
        if not self._ftp:
            raise RuntimeError("Not connected to FTP server.")
        os.makedirs(dest_folder, exist_ok=True)
        local_path = os.path.join(dest_folder, filename)
        with open(local_path, "wb") as f:
            self._ftp.retrbinary(f"RETR {filename}", f.write)
        return local_path

    def download_new_files(self, tracker, dest_folder: str) -> List[str]:
        """
        Download only files not yet seen by the tracker.
        Returns list of local paths of downloaded files.
        """
        all_files = self.list_files()
        downloaded = []
        for filename in all_files:
            if not tracker.has_seen(filename):
                local_path = self.download_file(filename, dest_folder)
                downloaded.append(local_path)
        return downloaded