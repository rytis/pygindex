"""Command line interface"""

import argparse
import sys
from .utils import Configuration


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pygi",
        description="Command line utility to interact with IG Index trading platform",
    )
    subparsers = parser.add_subparsers(dest="object", required=True)

    # ** instrument **
    parser_instrument = subparsers.add_parser("instrument", help="Instruments")
    subparsers_instrument = parser_instrument.add_subparsers(
        dest="instrument_command", required=True
    )
    # instrument -> search
    parser_instrument_search = subparsers_instrument.add_parser(
        "search", help="Search for markets"
    )
    parser_instrument_search.add_argument("term", type=str, help="Search term")
    # instrument -> get
    parser_instrument_get = subparsers_instrument.add_parser(
        "get", help="Get instrument details"
    )
    parser_instrument_get.add_argument("name", type=str, help="Instrument name")

    # ** positions **
    parser_positions = subparsers.add_parser("positions", help="Manage open positions")
    subparsers_positions = parser_positions.add_subparsers(
        dest="positions_command", required=True
    )
    # positions -> get
    parser_positions_get = subparsers_positions.add_parser(
        "get", help="Get open positions"
    )
    parser_positions_get.add_argument("--all")

    return parser


def parse_args(parser):
    return parser.parse_args()


def app():
    args = parse_args(build_parser())
    conf = Configuration.from_file()
    print(args)
    print(conf)
    sys.exit(0)
