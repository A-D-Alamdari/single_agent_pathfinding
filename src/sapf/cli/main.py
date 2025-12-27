from __future__ import annotations

import argparse
import sys

from ..cli.commands.convert import add_convert_subcommand
from ..cli.commands.generate import add_generate_subcommand
from ..cli.commands.run import add_run_subcommand
from ..cli.commands.validate import add_validate_subcommand


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sapf-cli",
        description="SAPF CLI: generate, validate, convert, and run single-agent pathfinding maps/algorithms.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_generate_subcommand(subparsers)
    add_validate_subcommand(subparsers)
    add_convert_subcommand(subparsers)
    add_run_subcommand(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))  # type: ignore[attr-defined]
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        # Centralized error formatting
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
