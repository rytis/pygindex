"""Client module"""
import time
from datetime import datetime
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import Dict, Union
import requests
from pygindex.models import (
    IGPriceResolution,
    IGUserAuth,
    IGAPIConfig,
    IGSession,
    IGResponse,
)


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


@dataclass
class IGInstrumentPrices:
    """Dataclass to hold price data structure"""

    instrument: IGInstrument
    instrument_type: str
    metadata: dict
    prices: list


class IGClient:
    """This is a class implementing basic IG Index API Client actions.

    :param auth: User authentication details
    :type auth: :class:`pygindex.models.IGUserAuth`
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

    def get_prices(
        self,
        instrument: IGInstrument,
        resolution: IGPriceResolution = IGPriceResolution.MINUTE,
        start_time: datetime = None,
        end_time: datetime = None,
        max_data_points: int = None,
    ) -> IGInstrumentPrices:
        """Retrieve historical data for the given instrument

        Example::

            c = IGClient()
            i = c.get_instrument("UA.D.AAPL.DAILY.IP")
            p = c.get_prices(i,
                             resolution=IGPriceResolution.HOUR_4,
                             start_time=datetime.now() - timedelta(days=1),
                             end_time=datetime.now())

        Produces the following data:

        Instrument type::

            "SHARES"

        Metadata::

            {
                "response": {
                    "allowance": {
                        "remainingAllowance": 9881,
                        "totalAllowance": 10000,
                        "allowanceExpiry": 597200
                    },
                    "size": 4,
                    "pageData": {
                        "pageSize": 4,
                        "pageNumber": 1,
                        "totalPages": 1
                    }
                }
            }

        Price data::

            [
                {
                    "snapshotTime": "2021/04/19 08:00:00",
                    "snapshotTimeUTC": "2021-04-19T07:00:00",
                    "openPrice": {
                        "bid": 13315.0,
                        "ask": 13444.0,
                        "lastTraded": null
                    },
                    "closePrice": {
                        "bid": 13391.0,
                        "ask": 13412.0,
                        "lastTraded": null
                    },
                    "highPrice": {
                        "bid": 13437.0,
                        "ask": 13448.0,
                        "lastTraded": null
                    },
                    "lowPrice": {
                        "bid": 13315.0,
                        "ask": 13380.0,
                        "lastTraded": null
                    },
                    "lastTradedVolume": 63705
                },
                {
                    "snapshotTime": "2021/04/19 12:00:00",
                    <...>
                },
                {
                    "snapshotTime": "2021/04/19 16:00:00",
                    <...>
                },
                {
                    "snapshotTime": "2021/04/19 20:00:00",
                    <...>
                }
            ]

        :param instrument: Instrument to get the price data for
        :type instrument: IGInstrument
        :param resolution: Resolution of the price data
        :type resolution: IGPriceResolution
        :param start_time: Start time of the lookup date range
        :type start_time: datetime.datetime
        :param end_time: End time of the lookup date range
        :type end_time: datetime.datetime
        :param max_data_points: Maximum data points to fetch. This is ignored if date range is specified
        :type max_data_points: int
        :return: Data structure that holds retrieved instrument prices
        :rtype: IGInstrumentPrices
        """

        epic = instrument.instrument["epic"]
        url = urljoin(f"{self._api.prices_url}/", epic)
        payload = {
            "resolution": resolution.value,
            "pageSize": 0,
        }
        if start_time and end_time:
            payload["from"] = start_time.isoformat(timespec="seconds")
            payload["to"] = end_time.isoformat(timespec="seconds")
        elif max_data_points:
            payload["max"] = max_data_points
        req = self._authenticated_request(
            url=url, method="get", data=payload, headers={"version": "3"}
        )
        data = {
            "instrument": instrument,
            "instrument_type": req.data["instrumentType"],
            "metadata": {"response": req.data["metadata"]},
            "prices": req.data["prices"],
        }
        return IGInstrumentPrices(**data)
