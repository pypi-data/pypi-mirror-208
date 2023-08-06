import json


class SonarAPIComponents(object):
    SEARCH_PROJECT_ENDPOINT = '/api/components/search_projects'

    def __init__(self, api=None):
        self._api = api

    def search_project(self, query, ps=50, facets=None, f=None):
        """
        get projets list.

        :param query: query to send
        :return: request response
        """
        # Build main data to post
        query = {
            'filter': query,
            'ps': ps,
            'facets': facets,
            'f': f
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.SEARCH_PROJECT_ENDPOINT, params=query)
        return res if res.status_code == 204 else json.loads(res.content)
    

