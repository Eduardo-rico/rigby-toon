import argparse

from .core import process_path

def main():
    parser = argparse.ArgumentParser(description="Rigby: The code raccoon.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser("parse", help="Parse python files to TOON format")
    parse_parser.add_argument("path", help="Path to file or directory")

    args = parser.parse_args()

    if args.command == "parse":
        process_path(args.path)

