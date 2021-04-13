"""Client module"""

import os
import time
from dataclasses import dataclass, field, fields
from typing import Dict
import requests


@dataclass
class IGUserAuth:
    """User Authentication data"""

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
        """Construct authentication headers"""
        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        return headers

    @property
    def auth_req_data(self) -> Dict[str, str]:
        """Authentication data used in requests"""
        data = {
            "identifier": self.username,
            "password": self.password,
            "encryptedPassword": None,
        }
        return data


@dataclass
class IGAPIConfig:
    """API configuration data"""

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
        """Session URL"""
        return f"{self.base_url}/session"

    @property
    def accounts_url(self) -> str:
        """Accounts URL"""
        return f"{self.base_url}/accounts"


@dataclass
class IGSession:
    """Session data"""

    cst: str = None
    security_token: str = None
    expires: int = 0


@dataclass
class IGResponse:
    """Response data"""

    data: Dict
    headers: Dict


class IGClient:
    """Client class"""

    def __init__(
        self, auth: IGUserAuth = None, api_config: IGAPIConfig = None
    ):
        self._auth = auth or IGUserAuth()
        self._api = api_config or IGAPIConfig()
        self._session = IGSession()

    @staticmethod
    def _request(
        url: str, method: str, headers: Dict, data: Dict
    ) -> IGResponse:
        """Make a request"""
        req = getattr(requests, method.lower())(
            url, headers=headers, json=data
        )
        response = IGResponse(data=req.json(), headers=req.headers)
        return response

    @property
    def _authentication_is_valid(self) -> bool:
        """Check is we're authenticated, and the authentication is current"""
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
        req = self._request(
            self._api.session_url, "post", headers=headers, data=data
        )
        if "Access-Control-Max-Age" in req.headers:
            self._session.expires = int(
                time.time() + int(req.headers["Access-Control-Max-Age"])
            )
        self._session.cst = req.headers["CST"]
        self._session.security_token = req.headers["X-SECURITY-TOKEN"]

    def get_session_details(self) -> dict:
        """Retrieve session details from the API"""
        req = self._authenticated_request(
            url=self._api.session_url, method="get"
        )
        return req.data

    def get_accounts(self) -> dict:
        """Retrieve account details from the API"""
        req = self._authenticated_request(
            url=self._api.accounts_url, method="get"
        )
        return req.data
