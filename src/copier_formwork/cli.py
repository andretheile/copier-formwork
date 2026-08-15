from __future__ import annotations

import argparse
import sys

from copier_formwork.server import serve_wizard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="copier-formwork",
        description="Generate a well-formed project (Copier template + localhost wizard).",
    )
    sub = parser.add_subparsers(dest="command")

    wizard = sub.add_parser("wizard", help="Open the localhost questionnaire (default).")
    wizard.add_argument("--host", default="127.0.0.1", help="Bind address (default 127.0.0.1).")
    wizard.add_argument("--port", type=int, default=8765)
    wizard.add_argument("--no-browser", action="store_true", help="Do not open a browser.")

    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if args.command is None:
        args.command = "wizard"
        args.host = "127.0.0.1"
        args.port = 8765
        args.no_browser = False

    if args.command == "wizard":
        serve_wizard(host=args.host, port=args.port, open_browser=not args.no_browser)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
