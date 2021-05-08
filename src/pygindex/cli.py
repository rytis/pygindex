"""Command line interface"""

import argparse
import json
import functools
import sys
import jinja2
from dataclasses import asdict
from .client import IGClient
from .models import IGUserAuth
from .utils import Configuration
from .utils import PluggableDecorator, method_labeler


cli_command = PluggableDecorator.build_decorator_class(
    set_name_callback=functools.partialmethod(method_labeler, label="_cli_command")
)


class CommandMeta(type):
    """Metaclass to create command classes.

    Currently the only purpose of this metaclass is to inject
    default class property that defines object cli name.

    Thus all classes that inherit from this metaclass are
    going to have `cli_name` property set to the lowercase
    name of the class, unless they override it.
    """

    def __new__(cls, *args, **kwargs):
        args[2].setdefault("cli_name", args[0].lower())
        cls_inst = super().__new__(cls, *args, **kwargs)
        return cls_inst


class GenericCommand(metaclass=CommandMeta):
    """Class to group and identify all CLI command classes.

    This is a simple approach to have "pluggable" architecture,
    and at this time this class is not responsible for anything else.

    The `docstrings` in child classes are important:
      * Class `docstring` is used as a CLI group description
      * Method decorated with :func:`cli_command` `docstring` is used as action group description
    """

    def __init__(self):
        self.jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader("pygindex"),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _display_data(self, output_format, template, data):
        if output_format == "json":
            output = json.dumps(data, indent=4, sort_keys=True)
        elif output_format == "text":
            template = self.jinja_env.get_template(template)
            output = template.render(d=data)
        print(output)


class InstrumentCommand(GenericCommand):
    """Instruments"""

    cli_name = "instrument"

    @cli_command
    def get(self, parser):
        """Get instrument details"""
        parser.add_argument("name", help="Instrument name")
        return self._get

    def _get(self, name, **kwargs):
        client = IGClient(get_auth_config())
        instrument_data = client.get_instrument(name)
        self._display_data(
            kwargs["format"], "cli_get_instrument.j2", asdict(instrument_data)
        )

    @cli_command
    def search(self, parser):
        """Search for instrument"""
        parser.add_argument("term", help="Search term")
        return self._search

    def _search(self, term, **kwargs):
        client = IGClient(get_auth_config())
        results = client.search_markets(term)
        self._display_data(kwargs["format"], "cli_search_instrument.j2", results)


class PositionsCommand(GenericCommand):
    """Manage positions"""

    cli_name = "positions"

    @cli_command
    def get(self, parser):
        """Get all positions"""
        parser.add_argument("--all", help="Get all")
        return self._get

    def _get(self, **kwargs):
        client = IGClient(get_auth_config())
        positions = client.get_positions()
        self._display_data(kwargs["format"], "cli_positions.j2", positions)


class AccountCommand(GenericCommand):
    """Query account details"""

    cli_name = "account"

    @cli_command
    def get(self, parser):
        """Get account information"""
        return self._get

    def _get(self, **kwargs):
        client = IGClient(get_auth_config())
        accounts = client.get_accounts()
        self._display_data(kwargs["format"], "cli_get_account.j2", accounts)


def register_command_parsers(cls, root_subparser):
    """Discover classes implementing command line objects and actions.
    Create new :mod:`argparse` parser for each discovered CLI object class.
    Register the created parser under the ``root_subparser``.
    Create new subparser to hold all commands, and create new parsers for
    each command.
    Register command callables for every action discovered.

    :param cls: Class that is used to discover all CLI object classes
    :param root_subparser: Base subparser where all command and action parsers will be registered
    :return: A map of callables for each (``object``, ``action``)
    """
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
    """Create and instance of :class:`argparse.ArgumentParser`

    :return: A tuple of created parser and subparser instances
    """
    parser = argparse.ArgumentParser(
        prog="pygi",
        description="Command line utility to interact with IG Index trading platform",
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format type"
    )
    subparser = parser.add_subparsers(dest="object", required=True)
    return parser, subparser


def build_dispatch_map(parser):
    """Create callable dispatch map.

    :param parser: Instance of initialised :mod:`argparse`
    :return: Map of callables for each CLI (``object``, ``action``) pair
    """
    dispatch_map = register_command_parsers(GenericCommand, parser)
    return dispatch_map


def parse_args(parser):
    """Parse command line arguments using provided parser.

    :param parser: Instance of initialised :mod:`argparse`
    :return: Namespace generated by :meth:`~argparse.ArgumentParser.parse_args`
    """
    return parser.parse_args()


def dispatch_command(args, dispatch_map):
    """Given a parsed arguments object and a dispatch map, call
    relevant callable for ``object`` and ``command`` pair.

    Pass on all other available arguments to the callable as a dictionary, but
    remove ``object`` and ``command`` entries.

    :param args: Object containing parsed arguments
    :param dispatch_map: Dictionary with callables for (``object``, ``command``) pairs
    """
    key = (args.object, args.command)
    cmd_args = {
        k: v for k, v in args.__dict__.items() if k not in ["object", "command"]
    }
    dispatch_map[key](**cmd_args)


def get_auth_config(platform=None):
    """Read configuration file and build an instance of :class:`IGUserAuth`

    :param platform: Optional platform selector, defaults to ``None`` in which
                     case a setting from configuration file will be used.
    :return: IG Authentication object
    """
    conf = Configuration.from_file()
    platform = platform or conf["platform"]["default"]
    auth_conf = conf["auth"][platform]
    ig_auth = IGUserAuth(**auth_conf)
    return ig_auth


def app():
    parser, subparser = init_parser()
    dispatch_map = build_dispatch_map(subparser)
    args = parse_args(parser)

    dispatch_command(args, dispatch_map)

    sys.exit(0)
