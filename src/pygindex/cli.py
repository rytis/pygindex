"""Command line interface"""

import argparse
import functools
import sys
from .utils import Configuration
from .utils import PluggableDecorator, method_labeler


cli_command = PluggableDecorator.build_decorator_class(
    set_name_callback=functools.partialmethod(method_labeler, label="_cli_command")
)


class CommandMeta(type):
    def __new__(cls, *args, **kwargs):
        args[2].setdefault("cli_name", args[0].lower())
        cls_inst = super().__new__(cls, *args, **kwargs)
        return cls_inst


class GenericCommand(metaclass=CommandMeta):
    pass


class InstrumentCommand(GenericCommand):
    """Instruments"""

    cli_name = "instrument"

    @cli_command
    def get(self, parser):
        """Get instrument details"""
        print("register instrument get")
        parser.add_argument("name", help="Instrument name")
        return self._get

    def _get(self):
        print("process instrument get")

    @cli_command
    def search(self, parser):
        """Search for instrument"""
        print("register instrument search")
        parser.add_argument("term", help="Search term")
        return self._search

    def _search(self):
        print("process instrument search")


class PositionsCommand(GenericCommand):
    """Manage positions"""

    cli_name = "positions"

    @cli_command
    def get(self, parser):
        """Get all positions"""
        print("register positions get")
        parser.add_argument("--all", help="Get all")
        return self._get

    def _get(self):
        print("process positions get")


def register_command_parsers(cls, root_subparser):
    dispatch_map = {}
    for command_cls in cls.__subclasses__():
        parser_cmd = root_subparser.add_parser(command_cls.cli_name,
                                               help=command_cls.__doc__)
        subparsers_cmd = parser_cmd.add_subparsers(
            dest=f"{command_cls.cli_name}_command",
            required=True
        )
        for action in command_cls._cli_command:
            obj, action = command_cls.cli_name, action
            parser_action = subparsers_cmd.add_parser(action,
                                                      help=getattr(command_cls, action).__doc__)
            dispatch_map[(obj, action)] = getattr(command_cls(), action)(parser_action)
    return dispatch_map


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pygi",
        description="Command line utility to interact with IG Index trading platform",
    )
    subparsers = parser.add_subparsers(dest="object", required=True)

    dispatch_map = register_command_parsers(GenericCommand, subparsers)
    print(dispatch_map)

    # # ** instrument **
    # parser_instrument = subparsers.add_parser("instrument", help="Instruments")
    # subparsers_instrument = parser_instrument.add_subparsers(
    #     dest="instrument_command", required=True
    # )
    # # instrument -> search
    # parser_instrument_search = subparsers_instrument.add_parser(
    #     "search", help="Search for markets"
    # )
    # parser_instrument_search.add_argument("term", type=str, help="Search term")
    # # instrument -> get
    # parser_instrument_get = subparsers_instrument.add_parser(
    #     "get", help="Get instrument details"
    # )
    # parser_instrument_get.add_argument("name", type=str, help="Instrument name")
    #
    # # ** positions **
    # parser_positions = subparsers.add_parser("positions", help="Manage open positions")
    # subparsers_positions = parser_positions.add_subparsers(
    #     dest="positions_command", required=True
    # )
    # # positions -> get
    # parser_positions_get = subparsers_positions.add_parser(
    #     "get", help="Get open positions"
    # )
    # parser_positions_get.add_argument("--all")

    return parser


def parse_args(parser):
    return parser.parse_args()


def app():
    args = parse_args(build_parser())
    conf = Configuration.from_file()
    print(args)
    print(conf)
    sys.exit(0)
