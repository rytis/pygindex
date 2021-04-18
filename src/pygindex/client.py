"""Client module"""

import os
import time
from urllib.parse import urljoin
from dataclasses import dataclass, field, fields
from typing import Dict, Union
import requests


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


class IGClient:
    """This is a class implementing basic IG Index API Client actions.

    :param auth: User authentication details
    :type auth: :class:`IGUserAuth`
    :param api_config: API configuration details
    :type api_config: :class:`IGAPIConf`
    """

    def __init__(self, auth: IGUserAuth = None, api_config: IGAPIConfig = None):
        self._auth = auth or IGUserAuth()
        self._api = api_config or IGAPIConfig()
        self._session = IGSession()

    @staticmethod
    def _request(url: str, method: str, headers: Dict, data: Dict) -> IGResponse:
        """Make an HTTP request against specified URL
        :param url: URL to perform the request against
        :param method: HTTP method type
        :param headers: HTTP Headers to send with the request
        :param data: Data to include in the HTTP request
        :return: Return an initialised response object
        :rtype: :class:`IGResponse`
        """
        if method.lower() == "get":
            req = getattr(requests, method.lower())(url, headers=headers, params=data)
        else:
            req = getattr(requests, method.lower())(url, headers=headers, json=data)
        response = IGResponse(data=req.json(), headers=req.headers)
        return response

    @property
    def _authentication_is_valid(self) -> bool:
        """Check is we're authenticated, and the authentication is current
        :return: ``True`` if authentication is current, ``False`` otherwise
        :rtype: bool
        """
        current_time = int(time.time())
        if self._session.expires < current_time:
            return False
        if not (self._session.cst and self._session.security_token):
            return False
        return True

    def _authenticated_request(
        self, url: str, method: str, headers: Dict = None, data: Dict = None
    ) -> IGResponse:
        """Authenticate with API if we don't have valid token"""
        if not self._authentication_is_valid:
            self._authenticate()
        if headers:
            hdrs = headers.copy()
        else:
            hdrs = {}
        hdrs.update(
            {
                "CST": self._session.cst,
                "X-SECURITY-TOKEN": self._session.security_token,
            }
        )
        hdrs.update(self._auth.auth_req_headers)
        req = self._request(url=url, method=method, headers=hdrs, data=data)
        return req

    def _authenticate(self):
        """
        Call IG API session URL to retrieve session authentication tokens
        """
        headers = self._auth.auth_req_headers
        data = self._auth.auth_req_data
        req = self._request(self._api.session_url, "post", headers=headers, data=data)
        if "Access-Control-Max-Age" in req.headers:
            self._session.expires = int(
                time.time() + int(req.headers["Access-Control-Max-Age"])
            )
        self._session.cst = req.headers["CST"]
        self._session.security_token = req.headers["X-SECURITY-TOKEN"]

    def get_session_details(self) -> dict:
        """This method retrieves IG API specific session details.

        Example::

            c = IGClient()
            s = c.get_session_details()

        Session details::

            {
              'clientId': 'XXXXXXXXX',
              'accountId': 'XXXXX',
              'timezoneOffset': 1,
              'locale': 'en_GB',
              'currency': 'GBP',
              'lightstreamerEndpoint': 'https://apd.marketdatasystems.com'
            }

        :return: Dictionary with session details as documented in `Session API`_
        :rtype: dict

        .. _Session API: https://labs.ig.com/rest-trading-api-reference/service-detail?id=600
        """
        req = self._authenticated_request(url=self._api.session_url, method="get")
        return req.data

    def get_accounts(self) -> dict:
        """This method retrieves account details

        Example::

            c = IGClient()
            s = c.get_accounts()

        Account details::

            {
                "accounts": [
                    {
                        "accountAlias": null,
                        "accountId": "XXXXX",
                        "accountName": "CFD",
                        "accountType": "CFD",
                        "balance": {
                            "available": 0.0,
                            "balance": 0.0,
                            "deposit": 0.0,
                            "profitLoss": 0.0
                        },
                        "canTransferFrom": true,
                        "canTransferTo": true,
                        "currency": "GBP",
                        "preferred": false,
                        "status": "ENABLED"
                    },
                    {
                        "accountAlias": null,
                        "accountId": "XXXXX",
                        "accountName": "Spread bet",
                        "accountType": "SPREADBET",
                        "balance": {
                            "available": 0.0,
                            "balance": 0.0,
                            "deposit": 0.0,
                            "profitLoss": 0.0
                        },
                        "canTransferFrom": true,
                        "canTransferTo": true,
                        "currency": "GBP",
                        "preferred": true,
                        "status": "ENABLED"
                    }
                ]
            }

        :return: Dictionary with all accounts available on the platform as
                 documented in `Accounts API`_
        :rtype: dict

        .. _Accounts API: https://labs.ig.com/rest-trading-api-reference/service-detail?id=619
        """
        req = self._authenticated_request(url=self._api.accounts_url, method="get")
        return req.data

    def get_positions(self) -> dict:
        """This method retrieves all positions for authenticated account from the API

        Example::

            c = IGClient()
            p = c.get_positions()

        Positions details::

            {
                "positions": [
                    {
                        "position": {
                            "contractSize": 1.0,
                            "createdDate": "2021/02/10 11:42:56:000",
                            "dealId": "DIAAAAGB25EY6AN",
                            "dealSize": 0.1,
                            "direction": "BUY",
                            "limitLevel": null,
                            "openLevel": 13664.0,
                            "currency": "GBP",
                            "controlledRisk": false,
                            "stopLevel": null,
                            "trailingStep": null,
                            "trailingStopDistance": null,
                            "limitedRiskPremium": null
                        },
                        "market": {
                            "instrumentName": "Apple Inc (All Sessions)",
                            "expiry": "DFB",
                            "epic": "UA.D.AAPL.DAILY.IP",
                            "instrumentType": "SHARES",
                            "lotSize": 1.0,
                            "high": 13498.0,
                            "low": 13324.0,
                            "percentageChange": -0.34,
                            "netChange": -46.0,
                            "bid": 13398.0,
                            "offer": 13411.0,
                            "updateTime": "21:59:15",
                            "delayTime": 0,
                            "streamingPricesAvailable": false,
                            "marketStatus": "EDITS_ONLY",
                            "scalingFactor": 1
                        }
                    },

                    [...]

                ]
            }

        :return: Dictionary with all positions with details as documented
                  in `Positions API`_
        :rtype: dict

        .. _Positions API: https://labs.ig.com/rest-trading-api-reference/service-detail?id=611
        """
        req = self._authenticated_request(url=self._api.positions_url, method="get")
        return req.data

    def search_markets(self, term) -> dict:
        """Search for markets on IG Index platform that match specified criteria

        Example::

            c = IGClient()
            m = c.search_markets("AAPL")

        This search yields a list of all matching products::

            {
                "markets": [
                    {
                        "epic": "UA.D.AAPL.DAILY.IP",
                        "instrumentName": "Apple Inc (All Sessions)",
                        "instrumentType": "SHARES",
                        "expiry": "DFB",
                        "high": 13498.0,
                        "low": 13324.0,
                        "percentageChange": -0.34,
                        "netChange": -46.0,
                        "updateTime": "04:50:07",
                        "updateTimeUTC": "03:50:07",
                        "bid": 13400.0,
                        "offer": 13408.0,
                        "delayTime": 0,
                        "streamingPricesAvailable": false,
                        "marketStatus": "EDITS_ONLY",
                        "scalingFactor": 1
                    },
                    [...]
                ]
            }

        :param term: Search term
        :type term: str
        :return: List of markets that matched search criteria
        """
        payload = {"searchTerm": term}
        req = self._authenticated_request(
            url=self._api.markets_url, method="get", data=payload
        )
        return req.data

    def get_instrument(self, instrument: Union[str, IGInstrument]) -> IGInstrument:
        """Retrieve instrument details

        For the description of all available fields and options please
        refer to IG Index `Market`_ documentation.

        .. _Market: https://labs.ig.com/rest-trading-api-reference/service-detail?id=594

        Example::

            c = IGClient()
            i = c.get_instrument("UA.D.AAPL.DAILY.IP")

        The above query will return an instance of :class:`IGInstrument` containing
        the following attributes:

            - :attr:`IGInstrument.dealing_rules`
            - :attr:`IGInstrument.instrument`
            - :attr:`IGInstrument.snapshot`

        Dealing rules data example::

            {
                "minStepDistance": {
                    "unit": "POINTS",
                    "value": 1.0
                },
                "minDealSize": {
                    "unit": "POINTS",
                    "value": 0.1
                },
                "minControlledRiskStopDistance": {
                    "unit": "PERCENTAGE",
                    "value": 5.0
                },
                "minNormalStopOrLimitDistance": {
                    "unit": "POINTS",
                    "value": 5.0
                },
                "maxStopOrLimitDistance": {
                    "unit": "PERCENTAGE",
                    "value": 90.0
                },
                "controlledRiskSpacing": {
                    "unit": "POINTS",
                    "value": 100.0
                },
                "marketOrderPreference": "AVAILABLE_DEFAULT_OFF"
            }

        Instrument data example::

            {
                "epic": "UA.D.AAPL.DAILY.IP",
                "expiry": "DFB",
                "name": "Apple Inc (All Sessions)",
                "forceOpenAllowed": true,
                "stopsLimitsAllowed": true,
                "lotSize": 1.0,
                "unit": "AMOUNT",
                "type": "SHARES",
                "controlledRiskAllowed": true,
                "streamingPricesAvailable": false,
                "marketId": "AAPL-US",
                "currencies": [
                    {
                        "code": "$.",
                        "name": "USD",
                        "symbol": "$",
                        "baseExchangeRate": 1.384415,
                        "exchangeRate": 0.77,
                        "isDefault": false
                    },
                    {
                        "code": "#.",
                        "name": "GBP",
                        "symbol": "\u00a3",
                        "baseExchangeRate": 1.0,
                        "exchangeRate": 1.0,
                        "isDefault": true
                    }
                ],
                "marginDepositBands": [
                    {
                        "min": 0,
                        "max": 324,
                        "margin": 20
                    },
                    {
                        "min": 324,
                        "max": 1782,
                        "margin": 20
                    },
                    {
                        "min": 1782,
                        "max": 5184,
                        "margin": 40
                    },
                    {
                        "min": 5184,
                        "max": null,
                        "margin": 75
                    }
                ],
                "margin": 20.0,
                "slippageFactor": {
                    "unit": "pct",
                    "value": 100.0
                },
                "openingHours": {
                    "marketTimes": [
                        {
                            "openTime": "09:00",
                            "closeTime": "01:00"
                        }
                    ]
                },
                "expiryDetails": {
                    "lastDealingDate": "06/04/29 21:00",
                    "settlementInfo": "DFBs settle on the Last Dealing Day at the closing market bid/offer price
                                       of the share, plus or minus half the IG spread. "
                },
                "rolloverDetails": null,
                "newsCode": "AAPL.O",
                "chartCode": "AAPL",
                "country": "US",
                "valueOfOnePip": null,
                "onePipMeans": null,
                "contractSize": null,
                "specialInfo": [
                    "MIN KNOCK OUT LEVEL DISTANCE",
                    "MAX KNOCK OUT LEVEL DISTANCE",
                    "DEFAULT KNOCK OUT LEVEL DISTANCE",
                    "Please note US (All Sessions) shares close early at 22:00 UK time on Friday evenings."
                ]
            }

        Snapshot data example::

            {
                "marketStatus": "EDITS_ONLY",
                "netChange": -46,
                "percentageChange": -0.34,
                "updateTime": "21:59:15",
                "delayTime": 0,
                "bid": 13398.0,
                "offer": 13411.0,
                "high": 13498.0,
                "low": 13324.0,
                "binaryOdds": null,
                "decimalPlacesFactor": 1,
                "scalingFactor": 1,
                "controlledRiskExtraSpread": 0
            }


        :param instrument: Instrument to retrieve. Possible options:

                           - IG Index specific instrument identifier (EPIC) as :class:`str`
                           - Existing instrument data structure, :class:`IGInstrument`
        :return: A fully populated instance of :class:`IGInstrument`
        :rtype: IGInstrument
        """

        epic = instrument if type(instrument) is str else instrument.instrument["epic"]
        url = urljoin(f"{self._api.markets_url}/", epic)
        req = self._authenticated_request(url=url, method="get")
        instrument_data = {
            "dealing_rules": req.data["dealingRules"],
            "instrument": req.data["instrument"],
            "snapshot": req.data["snapshot"],
        }
        return IGInstrument(**instrument_data)
