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
        parser.add_argument("name", help="Instrument name")
        return self._get

    def _get(self, name):
        print(f"process instrument get ({name})")

    @cli_command
    def search(self, parser):
        """Search for instrument"""
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
        parser.add_argument("--all", help="Get all")
        return self._get

    def _get(self):
        print("process positions get")


def register_command_parsers(cls, root_subparser):
    dispatch_map = {}
    for command_cls in cls.__subclasses__():
        parser_cmd = root_subparser.add_parser(
            command_cls.cli_name, help=command_cls.__doc__
        )
        subparsers_cmd = parser_cmd.add_subparsers(dest="command", required=True)
        for action in command_cls._cli_command:
            obj, action = command_cls.cli_name, action
            parser_action = subparsers_cmd.add_parser(
                action, help=getattr(command_cls, action).__doc__
            )
            dispatch_map[(obj, action)] = getattr(command_cls(), action)(parser_action)
    return dispatch_map


def init_parser():
    parser = argparse.ArgumentParser(
        prog="pygi",
        description="Command line utility to interact with IG Index trading platform",
    )
    subparser = parser.add_subparsers(dest="object", required=True)
    return parser, subparser


def build_dispatch_map(parser):
    dispatch_map = register_command_parsers(GenericCommand, parser)
    return dispatch_map


def parse_args(parser):
    return parser.parse_args()


def dispatch_command(args, dispatch_map):
    key = (args.object, args.command)
    cmd_args = {
        k: v for k, v in args.__dict__.items() if k not in ["object", "command"]
    }
    dispatch_map[key](**cmd_args)


def app():
    parser, subparser = init_parser()
    dispatch_map = build_dispatch_map(subparser)
    args = parse_args(parser)

    dispatch_command(args, dispatch_map)

    _ = Configuration.from_file()
    sys.exit(0)
