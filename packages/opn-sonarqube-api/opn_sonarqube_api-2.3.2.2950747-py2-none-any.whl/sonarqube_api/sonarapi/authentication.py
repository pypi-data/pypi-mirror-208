import json


class SonarAPIAuthentication(object):
    # Endpoint for resources and rules
    AUTH_VALIDATION_ENDPOINT = '/api/authentication/validate'

    def __init__(self, api=None):
        self._api = api

    def validate_authentication(self):
        """
        Validate the authentication credentials passed on client initialization.
        This can be used to test the connection, since API always returns 200.

        :return: True if valid
        """
        res = self._api._make_call('get', self.AUTH_VALIDATION_ENDPOINT).json()
        return res.get('valid', False)