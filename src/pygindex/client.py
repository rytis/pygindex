import requests
import os
import time
from urllib.parse import urljoin
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class IGUserAuth:
    api_key: str = None
    username: str = None
    password: str = None

    def __post_init__(self):
        for fld in self.__dataclass_fields__.keys():
            if getattr(self, fld) is None:
                env_var_name = "IG_{}".format(fld.upper())
                if env_var_name not in os.environ:
                    raise ValueError(f"Required argument '{fld}' or environment variable '{env_var_name}' not set")
                else:
                    setattr(self, fld, os.environ[env_var_name])

    @property
    def auth_req_headers(self) -> Dict[str, str]:
        headers = {"X-IG-API-KEY": self.api_key, "Content-Type": "application/json"}
        return headers

    @property
    def auth_req_data(self) -> Dict[str, str]:
        data = {"identifier": self.username, "password": self.password, "encryptedPassword": None}
        return data


@dataclass
class IGAPIConfig:
    platform: str = None
    base_url: str = field(init=False)

    def __post_init__(self):
        platform_urls = {"live": "https://api.ig.com/gateway/deal",
                         "demo": "https://demo-api.ig.com/gateway/deal"}
        if self.platform is None:
            self.platform = os.environ.get("IG_PLATFORM", default="live")
        if self.platform not in platform_urls.keys():
            raise ValueError(f"Unknown platform type: {self.platform} (valid options: 'live', 'demo')")
        else:
            self.base_url = platform_urls[self.platform]

    @property
    def session_url(self) -> str:
        return f"{self.base_url}/session"

    @property
    def accounts_url(self) -> str:
        return f"{self.base_url}/accounts"


@dataclass
class IGSession:
    cst: str = None
    security_token: str = None
    expires: int = 0


@dataclass
class IGResponse:
    data: Dict
    headers: Dict


class IGClient:

    def __init__(self, auth: IGUserAuth = None, api_config: IGAPIConfig = None):
        self._auth = auth or IGUserAuth()
        self._api = api_config or IGAPIConfig()
        self._session = IGSession()

    @staticmethod
    def _request(url: str, method: str, headers: Dict, data: Dict) -> IGResponse:
        r = getattr(requests, method.lower())(url, headers=headers, json=data)
        response = IGResponse(data=r.json(), headers=r.headers)
        return response

    @property
    def _authentication_is_valid(self) -> bool:
        current_time = int(time.time())
        if self._session.expires < current_time:
            return False
        if not (self._session.cst and self._session.security_token):
            return False
        return True

    def _authenticated_request(self, url: str, method: str, headers: Dict = None, data: Dict = None) -> IGResponse:
        if not self._authentication_is_valid:
            self._authenticate()
        if headers:
            hdrs = headers.copy()
        else:
            hdrs = {}
        hdrs.update({"CST": self._session.cst, "X-SECURITY-TOKEN": self._session.security_token})
        hdrs.update(self._auth.auth_req_headers)
        r = self._request(url=url, method=method, headers=hdrs, data=data)
        return r

    def _authenticate(self):
        """
        Call IG API session URL to retrieve session authentication tokens
        """
        headers = self._auth.auth_req_headers
        data = self._auth.auth_req_data
        r = self._request(self._api.session_url, "post", headers=headers, data=data)
        if "Access-Control-Max-Age" in r.headers:
            self._session.expires = int(time.time() + int(r.headers["Access-Control-Max-Age"]))
        self._session.cst = r.headers["CST"]
        self._session.security_token = r.headers["X-SECURITY-TOKEN"]

    def get_session_details(self):
        r = self._authenticated_request(url=self._api.session_url, method="get")
        return r.data

    def get_accounts(self):
        r = self._authenticated_request(url=self._api.accounts_url, method="get")
        return r.data
