"""
Entry point. Run with:
  python main.py          → CLI mode
  python main.py --gui    → GUI mode
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gui", action="store_true")
    args, remaining = parser.parse_known_args()

    if args.gui:
        from src.gui import main as gui_main
        gui_main()
    else:
        from src.cli import main as cli_main
        sys.argv = [sys.argv[0]] + remaining
        cli_main()


if __name__ == "__main__":
    main()