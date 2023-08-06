from pydantic import BaseModel
from uuid import uuid4

import platform
import sys
from contextlib import AbstractContextManager
from requests import Session, Response
from typing import List, Optional, Any

from dnastack.common.events import EventSource
from dnastack.common.logger import get_logger
from dnastack.constants import __version__
from dnastack.http.authenticators.abstract import Authenticator


class AuthenticationError(RuntimeError):
    """ Authentication Error """


class HttpError(RuntimeError):
    def __init__(self, response: Response):
        super(HttpError, self).__init__(response)

    @property
    def response(self) -> Response:
        return self.args[0]

    def __str__(self):
        response: Response = self.response
        return f'HTTP {response.status_code}: {response.text}'


class ClientError(HttpError):
    pass


class ServerError(HttpError):
    pass



class JsonPatch(BaseModel):
    op: str
    path: Optional[str]
    value: Optional[Any]


class RetryHistoryEntry(BaseModel):
    authenticator_index: int
    with_reauthentication: bool
    with_next_authenticator: bool
    encountered_http_status: int
    encountered_http_response: str
    resolution: str

    def __str__(self):
        return (f'>>> Auth #{self.authenticator_index}\n'
                f'>>> reauth: {self.with_reauthentication}\n'
                f'>>> use_next: {self.with_next_authenticator}\n\n'
                f'HTTP {self.encountered_http_status}\n\n{self.encountered_http_response}\n\n'
                f'[ → {self.resolution}]')


class HttpSession(AbstractContextManager):
    def __init__(self,
                 uuid: Optional[str] = None,
                 authenticators: List[Authenticator] = None,
                 suppress_error: bool = True,
                 enable_auth: bool = True):
        super().__init__()

        self.__id = uuid or str(uuid4())
        self.__logger = get_logger(f'{type(self).__name__}/{self.__id}')
        self.__authenticators = authenticators
        self.__session: Optional[Session] = None
        self.__suppress_error = suppress_error
        self.__enable_auth = enable_auth

        # This will inherit event types from
        self.__events = EventSource(['authentication-before',
                                     'authentication-ok',
                                     'authentication-failure',
                                     'authentication-ignored',
                                     'blocking-response-required',
                                     'blocking-response-ok',
                                     'blocking-response-failed',
                                     'initialization-before',
                                     'refresh-before',
                                     'refresh-ok',
                                     'refresh-failure',
                                     'session-restored',
                                     'session-not-restored',
                                     'session-revoked'],
                                    origin=self)

        if self.__authenticators:
            for authenticator in self.__authenticators:
                self.__events.set_passthrough(authenticator.events)

        if not self.__enable_auth:
            self.__logger.info('Authentication has been disable for this session.')

    @property
    def events(self) -> EventSource:
        return self.__events

    @property
    def _session(self) -> Session:
        if not self.__session:
            self.__session = Session()
            self.__session.headers.update({
                'User-Agent': self.generate_http_user_agent()
            })

        return self.__session

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.close()

    def submit(self,
               method: str,
               url: str,
               retry_with_reauthentication: bool = True,
               retry_with_next_authenticator: bool = False,
               authenticator_index: int = 0,
               retry_history: Optional[List[RetryHistoryEntry]] = None,
               **kwargs) -> Response:
        retry_history = retry_history or list()
        session = self._session

        logger = get_logger(f'{self.__logger.name}/{self.__id}')
        logger.debug(f'{method.upper()} {url} (AUTH: {"Enabled" if self.__enable_auth else "Disabled"})')

        authenticator: Optional[Authenticator] = None
        if self.__enable_auth:
            if self.__authenticators:
                # logger.debug(f'AUTH: authenticator => {authenticator_index + 1}/{len(self.__authenticators)}')
                # logger.debug(f'AUTH: retry_with_reauthentication => {retry_with_reauthentication}')
                # logger.debug(f'AUTH: retry_with_next_authenticator => {retry_with_next_authenticator}')

                if authenticator_index < len(self.__authenticators):
                    authenticator = self.__authenticators[authenticator_index]
                else:
                    logger.error(f'Failed to authenticate for {url}')
                    counter = 0
                    for retry in retry_history:
                        counter += 1
                        logger.error(f'Retry #{counter}:\n\n{retry}\n')

                    raise AuthenticationError('Exhausted all authentication methods but still unable to get successful '
                                              f'authentication for {url}')

                logger.debug(f'AUTH: session_id => {authenticator.session_id}')

                authenticator.before_request(session)
            else:
                logger.debug(f'AUTH: no authenticators configured')
        else:
            logger.debug(f'AUTH: the authentication has been disabled')
            self.events.dispatch('authentication-ignored', dict(method=method, url=url))

        http_method = method.lower()
        response = getattr(self._session, http_method)(url, **kwargs)

        logger.debug(f'Responded with HTTP {response.status_code} ({len(response.text)}B)')
        logger.debug(f'Response Body:\n{response.text}')

        if response.ok:
            return response
        else:
            if self.__suppress_error:
                logger.debug('Error suppressed by the caller of this method.')
                return response

            status_code = response.status_code

            if self.__enable_auth:
                if status_code in (401, 403) and authenticator:
                    authenticator.revoke()

                    retry = RetryHistoryEntry(url=url,
                                              authenticator_index=authenticator_index,
                                              with_reauthentication=retry_with_reauthentication,
                                              with_next_authenticator=retry_with_next_authenticator,
                                              encountered_http_status=status_code,
                                              encountered_http_response=response.text,
                                              resolution='')
                    retry_history.append(retry)

                    if retry_with_reauthentication:
                        # Initiate the reauthorization process.
                        retry.resolution = 'retry with re-authentication'

                        return self.submit(method,
                                           url,
                                           retry_with_reauthentication=False,
                                           retry_with_next_authenticator=True,
                                           authenticator_index=authenticator_index,
                                           retry_history=retry_history,
                                           **kwargs)
                    elif retry_with_next_authenticator:
                        retry.resolution = 'retry with the next authenticator'

                        return self.submit(method,
                                           url,
                                           retry_with_reauthentication=True,
                                           retry_with_next_authenticator=False,
                                           authenticator_index=authenticator_index + 1,
                                           retry_history=retry_history,
                                           **kwargs)
                    else:
                        raise RuntimeError('Invalid state')
                else:
                    # Non-access-denied error will be handled here.
                    self._raise_http_error(response)
            else:
                # No-auth requests will just throw an exception.
                self._raise_http_error(response)

    def get(self, url, **kwargs) -> Response:
        return self.submit('get', url, **kwargs)

    def post(self, url, **kwargs) -> Response:
        return self.submit('post', url, **kwargs)

    def delete(self, url, **kwargs) -> Response:
        return self.submit('delete', url, **kwargs)

    def json_patch(self, url, **kwargs) -> Response:
        headers = kwargs.setdefault('headers', {})
        headers['Content-Type'] = 'application/json-patch+json'
        return self.submit('patch', url, **kwargs)

    def close(self):
        if self.__session:
            self.__id = None
            self.__session.close()
            self.__session = None

    @property
    def authenticators(self):
        return self.__authenticators

    def _raise_http_error(self, response: Response):
        raise ClientError(response) if response.status_code < 500 else ServerError(response)

    def __del__(self):
        self.close()

    @staticmethod
    def generate_http_user_agent(comments: Optional[List[str]] = None) -> str:
        # NOTE: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
        interested_module_names = [
            'IPython',  # indicates that it is probably used in a notebook
            'unittest',  # indicates that it is used by a test code
        ]

        final_comments = [
            f'Platform/{platform.platform()}',  # OS information + CPU architecture
            'Python/{}.{}.{}'.format(*sys.version_info),  # Python version
            *(comments or list()),
            *[
                f'Module/{interested_module_name}'
                for interested_module_name in interested_module_names
                if interested_module_name in sys.modules
            ]
        ]

        return f'dnastack-client/{__version__} {" ".join(final_comments)}'.strip()
