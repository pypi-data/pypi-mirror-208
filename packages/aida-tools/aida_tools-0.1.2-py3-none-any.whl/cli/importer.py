import argparse
from typing import Tuple

def get_args() -> Tuple:
    parser = argparse.ArgumentParser(
        description="AIDA Tools",
        epilog="AIDA Tools"
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        help="Type of import",
        choices=["tommasoli", "autpe"],
        required=True
    )

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="File to import"
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress output"
    )

    args = parser.parse_args()

    return args.file, args.quiet
