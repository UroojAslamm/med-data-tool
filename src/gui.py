"""
GUI interface for the Medical Data Download Tool.
Built with tkinter following recognised UI design principles:
  - Visibility of system status (progress bar, live log)
  - User control (configurable settings)
  - Error prevention (validated inputs)
  - Feedback (colour-coded results)
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cli import run_pipeline


class MedDataGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Medical Trial Data Download Tool — Centrala University")
        self.root.geometry("750x600")
        self.root.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        # ── Title ──────────────────────────────────────────────────────────
        title = tk.Label(
            self.root,
            text="Medical Trial Data Download Tool",
            font=("Helvetica", 16, "bold"),
            pady=10
        )
        title.pack()

        subtitle = tk.Label(
            self.root,
            text="Centrala University — School of Medicine",
            font=("Helvetica", 10),
            fg="grey"
        )
        subtitle.pack()

        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=10, pady=5)

        # ── FTP Settings ───────────────────────────────────────────────────
        settings_frame = ttk.LabelFrame(self.root, text="FTP Server Settings", padding=10)
        settings_frame.pack(fill="x", padx=15, pady=5)

        # Row 1: Host + Port
        tk.Label(settings_frame, text="Host:").grid(row=0, column=0, sticky="e", padx=5)
        self.host_var = tk.StringVar(value="127.0.0.1")
        tk.Entry(settings_frame, textvariable=self.host_var, width=20).grid(row=0, column=1, sticky="w")

        tk.Label(settings_frame, text="Port:").grid(row=0, column=2, sticky="e", padx=5)
        self.port_var = tk.StringVar(value="2121")
        tk.Entry(settings_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, sticky="w")

        # Row 2: User + Pass
        tk.Label(settings_frame, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.user_var = tk.StringVar(value="ftpuser")
        tk.Entry(settings_frame, textvariable=self.user_var, width=20).grid(row=1, column=1, sticky="w")

        tk.Label(settings_frame, text="Password:").grid(row=1, column=2, sticky="e", padx=5)
        self.pass_var = tk.StringVar(value="ftppass")
        tk.Entry(settings_frame, textvariable=self.pass_var, show="*", width=20).grid(row=1, column=3, sticky="w")

        # ── Buttons ────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=8)

        self.run_btn = ttk.Button(
            btn_frame, text="▶  Run Download & Validate",
            command=self._start_pipeline, width=28
        )
        self.run_btn.pack(side="left", padx=5)

        ttk.Button(
            btn_frame, text="🗑  Clear Log",
            command=self._clear_log, width=14
        ).pack(side="left", padx=5)

        # ── Progress bar ───────────────────────────────────────────────────
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=15, pady=2)

        # ── Log output ─────────────────────────────────────────────────────
        log_frame = ttk.LabelFrame(self.root, text="Activity Log", padding=5)
        log_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.log_box = scrolledtext.ScrolledText(
            log_frame, font=("Courier", 9), state="disabled",
            bg="#1e1e1e", fg="#d4d4d4"
        )
        self.log_box.pack(fill="both", expand=True)

        # Colour tags
        self.log_box.tag_config("valid", foreground="#4ec94e")
        self.log_box.tag_config("invalid", foreground="#f44747")
        self.log_box.tag_config("info", foreground="#9cdcfe")
        self.log_box.tag_config("header", foreground="#dcdcaa")

        # ── Status bar ─────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            bd=1, relief="sunken", anchor="w", font=("Helvetica", 9)
        )
        status_bar.pack(fill="x", side="bottom")

    def _log(self, message: str, tag: str = ""):
        self.log_box.config(state="normal")
        self.log_box.insert("end", message + "\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    def _validate_inputs(self):
        try:
            port = int(self.port_var.get())
            assert 1 <= port <= 65535
        except (ValueError, AssertionError):
            messagebox.showerror("Invalid Input", "Port must be a number between 1 and 65535.")
            return False
        if not self.host_var.get().strip():
            messagebox.showerror("Invalid Input", "Host cannot be empty.")
            return False
        return True

    def _start_pipeline(self):
        if not self._validate_inputs():
            return
        self.run_btn.config(state="disabled")
        self.progress.start(10)
        self.status_var.set("Running...")
        self._log("=" * 55, "header")
        self._log("  Starting download pipeline...", "info")
        self._log("=" * 55, "header")

        thread = threading.Thread(target=self._run_in_thread, daemon=True)
        thread.start()

    def _run_in_thread(self):
        host = self.host_var.get().strip()
        port = int(self.port_var.get())
        user = self.user_var.get().strip()
        password = self.pass_var.get()

        # Monkey-patch print to redirect to GUI log
        import builtins
        original_print = builtins.print

        def gui_print(*args, **kwargs):
            msg = " ".join(str(a) for a in args)
            if "✓" in msg and "Valid" in msg:
                tag = "valid"
            elif "✗" in msg:
                tag = "invalid"
            elif "===" in msg:
                tag = "header"
            else:
                tag = "info"
            self.root.after(0, self._log, msg, tag)

        builtins.print = gui_print

        try:
            summary = run_pipeline(host, port, user, password, verbose=True)
        finally:
            builtins.print = original_print

        def finish():
            self.progress.stop()
            self.run_btn.config(state="normal")
            self.status_var.set(
                f"Done — Valid: {summary['valid']} | "
                f"Invalid: {summary['invalid']} | "
                f"Skipped: {summary['skipped']}"
            )
        self.root.after(0, finish)


def main():
    root = tk.Tk()
    app = MedDataGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()