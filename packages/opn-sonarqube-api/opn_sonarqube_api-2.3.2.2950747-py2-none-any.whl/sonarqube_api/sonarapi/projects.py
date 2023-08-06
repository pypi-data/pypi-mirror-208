import json


class SonarAPIProjects(object):
    #Endpoint for permission templates
    PROJECT_SEARCH_ENDPOINT = 'api/projects/search'

    def __init__(self, api=None):
        self._api = api

    def search(self, query):
        """
        search project

        :param query: Limit search to:
            component names that contain the supplied string
            component keys that contain the supplied string
        :return: request response
        """
        # Build main data to get
        params = {
            'q': query
        }

        # Make call (might raise exception) and return
        res = self._api._get_call(self.PROJECT_SEARCH_ENDPOINT, params=params)
        return res if res.status_code == 204 else json.loads(res.content)


