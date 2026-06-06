from __future__ import annotations

import argparse
import sys

from .employee_app import run_employee_app
from .employer_app import run_employer_app
from .startup import install_startup, uninstall_startup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="employee-check", description="Employee Check desktop monitoring app")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("employer", help="Run employer dashboard/server")
    subparsers.add_parser("employee", help="Run employee agent")

    startup = subparsers.add_parser("startup", help="Install or remove startup entries")
    startup_sub = startup.add_subparsers(dest="action")
    install = startup_sub.add_parser("install", help="Install startup entry")
    install.add_argument("role", choices=["employee", "employer"])
    uninstall = startup_sub.add_parser("uninstall", help="Remove startup entry")
    uninstall.add_argument("role", choices=["employee", "employer"])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "employer":
        run_employer_app()
        return 0
    if args.command == "employee":
        run_employee_app()
        return 0
    if args.command == "startup":
        if args.action == "install":
            path = install_startup(args.role)
            print(f"Installed startup entry: {path}")
            return 0
        if args.action == "uninstall":
            path = uninstall_startup(args.role)
            print(f"Removed startup entry if present: {path}")
            return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())

