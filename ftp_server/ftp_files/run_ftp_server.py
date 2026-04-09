"""
Local test FTP server using pyftpdlib.
Run this in a separate terminal before using the main tool.
"""

import os
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

def run():
    # Create the directory where FTP files will live
    ftp_root = os.path.join(os.path.dirname(__file__), "ftp_files")
    os.makedirs(ftp_root, exist_ok=True)

    authorizer = DummyAuthorizer()
    # Add a user: username, password, directory, permissions
    # "elradfmwMT" = full permissions
    authorizer.add_user("ftpuser", "ftppass", ftp_root, perm="elradfmwMT")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = range(60000, 60100)

    # Listen on localhost port 2121
    server = FTPServer(("127.0.0.1", 2121), handler)
    print("FTP server running on ftp://127.0.0.1:2121")
    print(f"Serving files from: {ftp_root}")
    print("Username: ftpuser | Password: ftppass")
    print("Press Ctrl+C to stop.")
    server.serve_forever()

if __name__ == "__main__":
    run()