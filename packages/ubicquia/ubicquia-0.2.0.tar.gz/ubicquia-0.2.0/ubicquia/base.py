"""Base

- AUTH_URL: URL for authentication based on default or env.
- BASE_URL: URL for API requests.
"""
import os
from abc import ABC, abstractmethod
import json
import logging
from pathlib import Path
from time import time
from typing import TypedDict

from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from requests import Session, Response
from requests.exceptions import HTTPError
from oauthlib.oauth2 import LegacyApplicationClient
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

logger = logging.getLogger(__name__)

AUTH_URL = os.getenv(
    'UBICQUIA_AUTH_URL',
    'https://auth.ubihub.ubicquia.com'
    '/auth/realms/ubivu-prd/protocol/openid-connect/token'
)

BASE_URL = os.getenv('UBICQUIA_BASE_URL', 'https://api.ubicquia.com/api')


class TokenUpdate(ABC):
    """Define implementation interface for Store Token.

    Define a way to save and obtains token from external storage systems.
    """
    @abstractmethod
    def save(self, token: dict) -> None:
        """Save token in external storage.

        Args:
            token: data to save

        Returns:
            None

        Raises:
        """

    @abstractmethod
    def retrive(self) -> dict:
        """Obtains token from storage.

        Write your own method to obtain or retrive token from external source.
        """


class DefaultTokenUpdateJsonFile(TokenUpdate):
    """Implementation for single JSON file to store the token in filesystem.

    This will be the default Session Token to be serialized as Token.
    """
    tmp_dir: Path = Path('./.tmp').resolve()
    filename: str = 'token.json'

    def save(self, token: dict) -> None:
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        with open(self.tmp_dir / self.filename, 'w') as j:
            json.dump(token, j)
        logger.debug('Save token in JSON file')

    def retrive(self) -> dict:
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.tmp_dir / self.filename, 'r') as j:
                _token = json.load(j)
        except FileNotFoundError:
            _token = {}
        return _token


class UbicquiaSession:
    """Generate a requests.Session handling the Oauth2 flow.

    Ubicquia login require: Oauth2 - Client Credentials.

    oauthlib for BackendApplicationClient doesn't use 'refresh_token' in token
    response but Auth server gives that.

    Refresh Token isn't interactive, so always requests an Access Token
    https://stackoverflow.com/a/58698729/4112006

    Attributes:
        auth_url: URL used for token and authentication.

    Args:
        client_id: client id from platform
        client_secret: secret from platform
        username: username used in platform
        password: password used in platform
        auth_url: authentication url
        token_update: implementation of stogare for token
    """

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 username: str,
                 password: str,
                 auth_url: str = AUTH_URL,
                 token_update: TokenUpdate = DefaultTokenUpdateJsonFile()
                 ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.auth_url = auth_url
        self.token_update = token_update
        self.auth = HTTPBasicAuth(username=self.client_id,
                                  password=self.client_secret)
        self.__token = {}

    @property
    def token(self) -> dict:
        return self.__token

    @token.setter
    def token(self, value: dict) -> None:
        """Token setter.

        Args:
            value: token data

        Returns:
            None.

        Raises:
            ValueError: if token is not a dict
        """
        if not isinstance(value, dict):
            raise ValueError('Value must be dict')
        self.__token = value

    def save_token(self, token: dict) -> None:
        if self.token_update:
            self.token_update.save(token=token)

    def obtain_token_session(self) -> None:
        """Obtain from server or from saved a token

        Generate a requests.Session for consecutive requests. Additionally,
        some extra http headers included.
        """
        # Loading saved token
        self.token = self.token_update.retrive()

        # Verify if expired
        if self.token:
            t1 = time()
            t0 = self.token['expires_at']
            if t1 - 10 > t0:
                logger.debug('Token has expired')
                self.token = {}

        # Requesting new token
        if not self.token:
            logger.info('Request new token: Oauth fetch')
            self.oauth = OAuth2Session(
                client=LegacyApplicationClient(client_id=self.client_id),
            )
            self.token = self.oauth.fetch_token(
                token_url=self.auth_url,
                auth=self.auth,
                username=self.username,
                password=self.password,
                # client_id=self.client_id,
                client_secret=self.client_secret
            )
            # if it's ok, save the current token
            logger.debug('Save the token')
            self.save_token(self.token)
        else:
            self.oauth: Session = OAuth2Session(
                client=LegacyApplicationClient(client_id=self.client_id),
                token=self.token
            )
        # Oauth2 session set the corret headers for http request calls
        self.client: Session = self.oauth
        #
        # Configure headers for requests
        # Standard:
        self.client.headers.update({'Accept': 'application/json'})
        # Ubicquia API Docs show:
        # self.client.headers.update({'accept': 'application/json'})
        # print(f'self.client.headers {self.client.headers}')
        # import pdb; pdb.set_trace()

    def raw_req(self, *args, **kwargs) -> Response:
        """Returns a Respose object from requests.

        Args:
            *args, **kwargs: parameters passed to requests.request

        Return:
            Response object from requests module.

        Raises:
            HTTP Errors from requests.
        """
        self.obtain_token_session()
        return self.client.request(*args, **kwargs)

    def req(self, *args, **kwargs) -> dict:
        """Make a HTTP request to server.

        Wrapper for requests. Use this method as it were

        .. code:: python

            requests.request(*args, **kwargs)

        Args:
            args, kwargs: same as requests.request(...)

        Returns:
            dict: response data

        Raises:
            HTTPError:
        """
        self.obtain_token_session()
        r = self.client.request(*args, **kwargs)
        # from  pprint import pprint
        # print( f'request.headers = {r.request.headers}')
        # print( f'request.body = {r.request.body}')
        # pprint( r.json())
        # import pdb; pdb.set_trace()
        try:
            data = r.json()
        except json.decoder.JSONDecodeError:
            data = {}
        try:
            r.raise_for_status()
        except HTTPError:
            logger.exception(f'HTTPError handled. Error json={data}')
            raise
        return data

    def manual_refresh_token(self):
        """
        UNUSED: This method is not used.
        Using Oauth refres_token
        """
        logger.info('Refresh_token')
        extra = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        try:
            new_token = self.oauth.refresh_token(self.auth_url, **extra)
        except InvalidGrantError:
            logger.error('InvalidGrantError')
        else:
            self.token = new_token

    def __str__(self):
        return f'UbicquiaSession for {self.username}'


class PaginationDict(TypedDict):
    page: str
    per_page: str


class Endpoint:
    """Define common endpoint class for SDK.

    Attributes:
        base_url: URL obtained from Session
    """

    def __init__(self, session: UbicquiaSession):
        """
        Args:
            session: generated by Oauthlib
        """
        self.base_url = BASE_URL
        self.base_url_v2 = BASE_URL + '/v2'
        self.session = session

    def pagination(self,
                   page: int = 1,
                   per_page: int = 15) -> PaginationDict:
        """Handle pagination.

        Filter by pagination parameters. Example unpack to combine pagination
        ** self.pagination(** pagination)

        Args:
            page: (default to 1) page number
            per_page: (default to 15) number of items per page

        Returns:
            PaginationDict: example {'page': 1, 'per_page': 15}

        Raises:
            TypeError: if invalid arguments provided,
                method got an unexpected keyword argument
        """
        return PaginationDict(page=page, per_page=per_page)
