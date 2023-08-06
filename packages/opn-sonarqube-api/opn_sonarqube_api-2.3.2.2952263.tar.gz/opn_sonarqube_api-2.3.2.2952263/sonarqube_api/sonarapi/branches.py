import json


class SonarAPIBranches(object):
    #Endpoint for permission templates
    PROJECT_BRANCHES_ENDPOINT = 'api/project_branches/list'

    def __init__(self, api=None):
        self._api = api

    def get(self, project):
        """
        get project branches

        :param project: List the branches of a project.
        :return: request response
        """
        # Build main data to post
        params = {
            'project': project
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('get', self.PROJECT_BRANCHES_ENDPOINT, params=params)
        return res if res.status_code == 204 else json.loads(res.content)


