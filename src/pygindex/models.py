import os
from dataclasses import dataclass, fields, field
from enum import Enum, unique
from typing import Dict


class DocEnum(Enum):
    def __new__(cls, value, doc=None):
        self = object.__new__(cls)  # calling super().__new__(value) here would fail
        self._value_ = value
        if doc is not None:
            self.__doc__ = doc
        return self


@unique
class IGPriceResolution(DocEnum):
    """Set of values defining available resolution settings
    when requesting historical price data.

    Resolution means that the returned price values are going to be aggregates
    for the time period specified by the resolution value.

    For example, selecting :enum:`IGPriceResolution.WEEK` will return max/min open/close values for
    each week, whereas :enum:`IGPriceResolution.HOUR_3` will return max/min open/close values for
    every 3 hour period.
    """

    SECOND = "SECOND", "1 second"
    HOUR = "HOUR", "1 hour"
    HOUR_2 = "HOUR_2", "2 hours"
    HOUR_3 = "HOUR_3", "3 hours"
    HOUR_4 = "HOUR_4", "4 hours"
    DAY = "DAY", "1 day"
    WEEK = "WEEK", "1 week"
    MONTH = "MONTH", "1 month"
    MINUTE = "MINUTE", "1 minute"
    MINUTE_2 = "MINUTE_2", "2 minutes"
    MINUTE_3 = "MINUTE_3", "3 minutes"
    MINUTE_5 = "MINUTE_5", "5 minutes"
    MINUTE_10 = "MINUTE_10", "10 minutes"
    MINUTE_15 = "MINUTE_15", "15 minutes"
    MINUTE_30 = "MINUTE_30", "30 minutes"


@dataclass
class IGUserAuth:
    """Dataclass to hold User Authentication data

    Configuration can be provided during initialisation,
    alternatively the following environment variables
    will be looked up if no arguments were provided:
    :data:`IG_{UPPERCASE_PARAM_NAME}`, for example: :data:`IG_API_KEY`

    :param api_key: API key
    :type api_key: str
    :param username: Username
    :type username: str
    :param password: Password
    :type password: str
    """

    api_key: str = None
    username: str = None
    password: str = None

    def __post_init__(self):
        """Attempt to fill in configuration from env vars"""
        for fld in fields(self):
            if getattr(self, fld.name) is None:
                env_var_name = "IG_{}".format(fld.name.upper())
                if env_var_name not in os.environ:
                    raise ValueError(
                        f"Required argument '{fld.name}' or environment "
                        f"variable '{env_var_name}' not set"
                    )
                setattr(self, fld.name, os.environ[env_var_name])

    @property
    def auth_req_headers(self) -> Dict[str, str]:
        """Construct authentication headers

        These headers need to be sent with every request made to
        IG Index API

        :returns: Dictionary containing required authentication headers
        :rtype: dict
        """
        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        return headers

    @property
    def auth_req_data(self) -> Dict[str, str]:
        """Construct Authentication data

        Constructs authentication data that will be used to obtain
        authentication key from IG Index API

        :returns: Dictionary containing authentication details
        :rtype: dict
        """
        data = {
            "identifier": self.username,
            "password": self.password,
            "encryptedPassword": None,
        }
        return data


@dataclass
class IGAPIConfig:
    """Dataclass for API configuration

    Configuration is provided during initialisation, otherwise, if no
    value is specified we will try to look up environment variable
    called :data:`IG_PLATFORM`.

    :param platform: Specify what platform to use. Available options are
                     :data:`live` - to access live trading platform, or
                     :data:`demo` - to access demo trading platform
    :type platform: str
    :param base_url: The value is resolved based on the ``platform`` value.
    :type base_url: str
    """

    platform: str = None
    base_url: str = field(init=False)

    def __post_init__(self):
        """Attempt to fill in configuration from env vars"""
        platform_urls = {
            "live": "https://api.ig.com/gateway/deal",
            "demo": "https://demo-api.ig.com/gateway/deal",
        }
        if self.platform is None:
            self.platform = os.environ.get("IG_PLATFORM", default="live")
        if self.platform not in platform_urls.keys():
            raise ValueError(
                f"Unknown platform type: {self.platform} "
                f"(valid options: 'live', 'demo')"
            )
        self.base_url = platform_urls[self.platform]

    @property
    def session_url(self) -> str:
        """Return IG Index API Session URL

        :returns: Session API URL
        :rtype: str
        """
        return f"{self.base_url}/session"

    @property
    def accounts_url(self) -> str:
        """Return IG Index API Accounts URL

        :returns: Accounts API URL
        :rtype: str
        """
        return f"{self.base_url}/accounts"

    @property
    def positions_url(self) -> str:
        """Returns IG Index API Positions URL

        :returns: Positions API URL
        :rtype: str
        """
        return f"{self.base_url}/positions"

    @property
    def markets_url(self) -> str:
        """Returns IG Index API Markets URL

        This endpoint is used for multiple purposes:

            * Lookup details of a selection of epics
            * Lookup details of individual epic
            * Search for epics

        :returns: Markets API URL
        :rtype: str
        """
        return f"{self.base_url}/markets"

    @property
    def prices_url(self) -> str:
        """Returns IG Index Prices URL

        :return: Prices API URL
        :rtype: str
        """
        return f"{self.base_url}/prices"


@dataclass
class IGSession:
    """Dataclass to hold Session data

    All values are retrieved after making an authentication
    call to IG Index API

    :param cst: CST
    :type cst: str
    :param security_token: Security token
    :type security_token: str
    :param expires: Expiration timestamp
    :type expires: int
    """

    cst: str = None
    security_token: str = None
    expires: int = 0


@dataclass
class IGResponse:
    """Dataclass to hold request Response data

    :param data: Response data
    :type data: dict
    :param headers: Response headers
    :type headers: dict
    """

    data: Dict
    headers: Dict


@dataclass
class IGInstrument:
    """Dataclass to hold IG Index Instrument data

    IG Instrument is a financial instrument based on some underlying
    financial market instrument. IG Instruments do not represent
    real world identifiers and are used exclusively on IG Index platform.

    More information about the IG Index terms can be found
    on their `Glossary`_ page.

    .. _Glossary: https://labs.ig.com/glossary

    :param dealing_rules: Data structure defining instrument dealing rules
    :type dealing_rules: dict
    :param instrument: Instrument definition
    :type instrument: dict
    :param snapshot: Snapshot data
    :type snapshot: dict
    """

    dealing_rules: dict
    instrument: dict
    snapshot: dict
