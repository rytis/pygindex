"""Command line interface"""

import argparse
import arrow
import json
import functools
import sys
import jinja2
from typing import Tuple, Callable
from .client import IGClient
from .models import IGUserAuth, IGPriceResolution, IGAPIConfig
from .utils import Configuration, PyGiJSONEncoder
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
            output = json.dumps(data, indent=4, sort_keys=True, cls=PyGiJSONEncoder)
        elif output_format == "text":
            template = self.jinja_env.get_template(template)
            output = template.render(d=data)
        print(output)


class InstrumentCommand(GenericCommand):
    """Instruments"""

    cli_name = "instrument"

    @cli_command
    def get(self, parser: argparse.ArgumentParser) -> Callable[[str, dict], None]:
        """Get instrument details"""
        parser.add_argument("name", help="Instrument name")
        parser.add_argument("-p", "--prices", action="store_true", help="Retrieve price data.")
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-r", "--range", nargs=2, metavar=("FROM", "TO"), help="Date time range to retrieve price data."
        )
        group.add_argument(
            "-m", "--max-num", help="Max number of data points to retrieve. Ignored, if range is specified."
        )
        parser.add_argument(
            "-n",
            "--resolution",
            default="MINUTE",
            choices=[r.value for r in IGPriceResolution],
            help="Resolution of the requested prices.",
        )
        return self._get

    @staticmethod
    def _parse_date(date_expr: str):
        now = arrow.utcnow().to("local")
        if date_expr.lower() == "now":
            return now.datetime
        try:
            ts = arrow.get(date_expr)
        except arrow.parser.ParserError:
            try:
                ts = now.dehumanize(date_expr)
            except ValueError:
                print("Do not know how to parse datetime: {}".format(date_expr))
                sys.exit(1)
        return ts.datetime

    def _get(self, name: str, **kwargs):
        client = IGClient(get_auth_config(), get_api_config())
        instrument_data = client.get_instrument(name)
        if kwargs["prices"]:
            ts_from, ts_to = None, None
            max_points = None
            resolution = IGPriceResolution.MINUTE
            if kwargs["range"]:
                ts_from, ts_to = map(self._parse_date, kwargs["range"])
            elif kwargs["max_num"]:
                max_points = kwargs["max_num"]
            if kwargs["resolution"]:
                resolution = getattr(IGPriceResolution, kwargs["resolution"])
            instrument_prices = client.get_prices(
                instrument_data, start_time=ts_from, end_time=ts_to, max_data_points=max_points, resolution=resolution
            )
        else:
            instrument_prices = None
        data = dict(data=instrument_data, prices=instrument_prices)
        self._display_data(kwargs["format"], "cli_get_instrument.j2", data)

    @cli_command
    def search(self, parser):
        """Search for instrument"""
        parser.add_argument("term", help="Search term")
        return self._search

    def _search(self, term, **kwargs):
        client = IGClient(get_auth_config(), get_api_config())
        results = client.search_markets(term)
        self._display_data(kwargs["format"], "cli_search_instrument.j2", results)


class PositionsCommand(GenericCommand):
    """Manage positions"""

    cli_name = "positions"

    @cli_command
    def get(self, parser: argparse.ArgumentParser):
        """Get all positions"""
        parser.add_argument("--all", help="Get all")
        return self._get

    def _get(self, **kwargs):
        client = IGClient(get_auth_config(), get_api_config())
        positions = client.get_positions()
        self._display_data(kwargs["format"], "cli_get_positions.j2", positions)

    @cli_command
    def close(self, parser: argparse.ArgumentParser):
        """Close position"""
        parser.add_argument("deal_id", help="Deal ID")
        return self._close

    def _close(self, **kwargs):
        deal_id = kwargs["deal_id"]
        client = IGClient(get_auth_config(), get_api_config())
        print(f"Closing {deal_id}")
        result = client.close_position(deal_id)
        print(f"{result}")


class AccountCommand(GenericCommand):
    """Query account details"""

    cli_name = "account"

    @cli_command
    def get(self, parser):
        """Get account information"""
        return self._get

    def _get(self, **kwargs):
        client = IGClient(get_auth_config(), get_api_config())
        accounts = client.get_accounts()
        session = client.get_session_details()
        data = dict(accounts=accounts, session=session)
        self._display_data(kwargs["format"], "cli_get_account.j2", data)


def register_command_parsers(cls: type, root_subparser: argparse.Namespace) -> dict:
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
        parser_cmd = root_subparser.add_parser(command_cls.cli_name, help=command_cls.__doc__)
        subparsers_cmd = parser_cmd.add_subparsers(dest="command", required=True)
        for action in command_cls._cli_command:
            obj, action = command_cls.cli_name, action
            parser_action = subparsers_cmd.add_parser(action, help=getattr(command_cls, action).__doc__)
            dispatch_map[(obj, action)] = getattr(command_cls(), action)(parser_action)
    return dispatch_map


def init_parser() -> Tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    """Create an instance of :class:`argparse.ArgumentParser`

    :return: A tuple of created parser and subparser instances
    """
    parser = argparse.ArgumentParser(
        prog="pygi",
        description="Command line utility to interact with IG Index trading platform",
    )
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format type")
    subparser = parser.add_subparsers(dest="object", required=True)
    return parser, subparser


def build_dispatch_map(parser: argparse.Namespace) -> dict:
    """Create callable dispatch map.

    :param parser: Instance of initialised :mod:`argparse`
    :return: Map of callables for each CLI (``object``, ``action``) pair
    """
    dispatch_map = register_command_parsers(GenericCommand, parser)
    return dispatch_map


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Parse command line arguments using provided parser.

    :param parser: Instance of initialised :mod:`argparse`
    :return: Namespace generated by :meth:`~argparse.ArgumentParser.parse_args`
    """
    return parser.parse_args()


def dispatch_command(args: argparse.Namespace, dispatch_map: dict):
    """Given a parsed arguments object and a dispatch map, call
    relevant callable for ``object`` and ``command`` pair.

    Pass on all other available arguments to the callable as a dictionary, but
    remove ``object`` and ``command`` entries.

    :param args: Object containing parsed arguments
    :param dispatch_map: Dictionary with callables for (``object``, ``command``) pairs
    """
    key = (args.object, args.command)
    cmd_args = {k: v for k, v in args.__dict__.items() if k not in ["object", "command"]}
    dispatch_map[key](**cmd_args)


def get_config() -> dict:
    """Build configuration dictionary

    :return: Dictionary containing configuration settings
    """
    conf = Configuration.from_file()
    return conf


def get_api_config(platform: str = None) -> IGAPIConfig:
    """Create API configuration object

    :param platform: Optional platform selector, defaults to ``None`` in which
                     case a setting from configuration file will be used.
    :return: IG API configuration object
    """
    conf = get_config()
    platform = platform or conf["platform"]["default"]
    ig_api = IGAPIConfig(platform)
    return ig_api


def get_auth_config(platform: str = None) -> IGUserAuth:
    """Create authentication object

    :param platform: Optional platform selector, defaults to ``None`` in which
                     case a setting from configuration file will be used.
    :return: IG Authentication object
    """
    conf = get_config()
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
