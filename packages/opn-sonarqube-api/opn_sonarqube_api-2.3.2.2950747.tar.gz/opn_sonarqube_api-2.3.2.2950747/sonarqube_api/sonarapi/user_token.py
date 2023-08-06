import json


class SonarAPIUserToken(object):
    #Endpoint for permission templates
    USER_TOKEN_GENERATE_ENDPOINT = '/api/user_tokens/generate'
    USER_TOKEN_SEARCH_ENDPOINT = '/api/user_tokens/search'
    USER_TOKEN_REVOKE_ENDPOINT = '/api/user_tokens/revoke'

    def __init__(self, api=None):
        self._api = api

    def generate_token(self, token_name, user_login):
        """
        Create user token.

        :param token_name: name of the token to generate
        :param user_login: user to generate token for
        :return: request response
        """
        # Build main data to post
        data = {
            'name': token_name,
            'login': user_login
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.USER_TOKEN_GENERATE_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def revoke_token(self, token_name, user_login):
        """
        Revoke user token.

        :param token_name: name of the token to revoke
        :param user_login: user to generate token for
        :return: request response
        """
        # Build main data to post
        data = {
            'name': token_name,
            'login': user_login
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.USER_TOKEN_REVOKE_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def search_token(self, user_login):
        """
        List existing token for user.
        """
        data = {
            'login': user_login
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.USER_TOKEN_SEARCH_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)
