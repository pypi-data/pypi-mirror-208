import json


class SonarAPISettings(object):
    #Endpoint for permission templates
    SET_ENDPOINT = '/api/settings/set'
    GET_ENDPOINT = '/api/settings/values'

    def __init__(self, api=None):
        self._api = api

    def get(self, key):
        """
        Create/update setting.

        :param key: name of the setting to get
        :return: request response
        """
        # Build main data to post
        data = {
            'keys': key
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.GET_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def set(self, key, value):
        """
        Retrieve setting.

        :param key: name of the setting to update
        :param value: value to set
        :return: request response
        """
        # Build main data to post
        data = {
            'key': key,
            'value': value
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.SET_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

