"""
This module contains the SonarAPIHandler, used for communicating with the
SonarQube server web service API.
"""
import requests
from .exceptions import ClientError, AuthError, ValidationError, ServerError


class SonarAPIHandler(object):

    def __init__(self, host=None, port=None, user=None, password=None,
                 base_path=None, token=None, headers=None):
        """
        Set connection info and session, including auth (if user+password
        and/or auth token were provided).
        """
        self._host = host
        self._port = port
        self._base_path = base_path
        self._session = requests.Session()
        self._headers = headers

        # Prefer revocable authentication token over username/password if
        # both are provided
        if token:
            self._session.auth = token, ''
        elif user and password:
            self._session.auth = user, password

    def get_url(self, endpoint):
        """
        Return the complete url including host and port for a given endpoint.

        :param endpoint: service endpoint as str
        :return: complete url (including host and port) as str
        """
        return '{}:{}{}{}'.format(self._host, self._port, self._base_path, endpoint)

    def _make_call(self, method, endpoint, data={}, params={}, files=None, headers=None):
        """
        Make the call to the service with the given method, queryset and data,
        using the initial session.

        Note: data is not passed as a single dictionary for better testability
        (see https://github.com/kako-nawao/python-sonarqube-api/issues/15).

        :param method: http method (get, post, put, patch)
        :param endpoint: relative url to make the call
        :param data: queryset or body
        :return: response
        """
        # Get method and make the call
        call = getattr(self._session, method.lower())
        url = self.get_url(endpoint)

        _headers = {}
        if headers is not None:
            _headers.update(headers)
        if self._headers is not None:
            _headers.update(self._headers)
        res = call(url, data=data, params=params, files=files, headers=_headers)

        # Analyse response status and return or raise exception
        # Note: redirects are followed automatically by requests
        if res.status_code < 300:
            # OK, return http response
            return res

        elif res.status_code == 400:
            # Validation error
            msg = ', '.join(e['msg'] for e in res.json()['errors'])
            raise ValidationError(msg)

        elif res.status_code in (401, 403):
            # Auth error
            raise AuthError(res.reason)

        # elif res.status_code == 404:
        #     raise ClientError(res.reason)

        elif res.status_code < 500:
            # Other 4xx, generic client error
            raise ClientError(res.reason)

        else:
            # 5xx is server error
            raise ServerError(res.reason)

    def _get_call(self, endpoint, params):
        """
        Specifically make the get call to the service, queryset and data,
        using the initial session.

        :param endpoint: relative url to make the call
        :param params: queryset or body
        :return: response
        """
        url = self.get_url(endpoint)
        combined=url+params

        res = requests.get(combined, auth=self._session.auth)

        if res.status_code < 300:
            return res
        elif res.status_code == 400:
            msg = ', '.join(e['msg'] for e in res.json()['errors'])
            raise ValidationError(msg)
        elif res.status_code in (401, 403):
            raise AuthError(res.reason)
        elif res.status_code < 500:
            raise ClientError(res.reason)
        else:
            raise ServerError(res.reason)
