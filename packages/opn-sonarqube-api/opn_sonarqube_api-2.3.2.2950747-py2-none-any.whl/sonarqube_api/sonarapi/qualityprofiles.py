import json
import re

class SonarAPIQualityProfile(object):
    PROJECTS_ENDPOINT = '/api/qualityprofiles/projects'
    RULES_ACTIVATION_ENDPOINT = '/api/qualityprofiles/activate_rule'
    CREATE_QUALITY_PROFILE_ENDPOINT = '/api/qualityprofiles/create'
    SEARCH_QUALITY_PROFILE_ENDPOINT = '/api/qualityprofiles/search'
    ADD_PROJECT_TO_QUALITY_PROFILE_ENDPOINT = '/api/qualityprofiles/add_project'
    RESTORE_QUALITY_PROFILE_FROM_XML_ENDPOINT = '/api/qualityprofiles/restore'
    DELETE_QUALITY_PROFILE_ENDPOINT = '/api/qualityprofiles/delete'

    def __init__(self, api=None):
        self._api = api

    def project(self, key, query, ps=50, selected='all'):
        """
        get projets list.

        :param key: Id of the qualityprofile
        :param query: query to send
        :param ps: pageSize
        :param selected: all/selected/deselected
        :return: request response
        """
        # Build main data to get
        combined="?key="+key+"&ps="+ps+"&selected="+selected+"&q="+query

        # Make call (might raise exception) and return
        res = self._api._get_call(self.PROJECTS_ENDPOINT, params=combined)
        return res if res.status_code == 204 else json.loads(res.content)

    def restore_quality_profile_from_xml(self, backup, project_name):
        """
        Create a quality profile with rules from a xml file

        :param project_name: name of the project, used to name the profile
        :param backup: contents of xml file to config quality profile
        :return:
        """

        # Retrieve the language in the xml
        r = re.search('<language>(.*)</language>', backup)
        if r is not None:
            language = r.group(1)
        else:
            print('error no language set in xml')

        # Replace the profile name by the project name
        backup = re.sub(r"<name>(.*?)</name>", r"<name>" + project_name + "</name>", backup)

        # Check if the qg exists already, and if so, deletes it
        existing_qp = self.search_quality_profile(project_name)
        if existing_qp is not None and existing_qp["profiles"] is not None:
            for profile in existing_qp["profiles"]:
                if profile['name'] == project_name and profile['language'] == language:
                    self.delete_quality_profile(project_name, language)

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.RESTORE_QUALITY_PROFILE_FROM_XML_ENDPOINT, files=dict(backup=backup))
        return res if res.status_code == 204 else json.loads(res.content)

    def search_quality_profile(self, profile_name):
        """

        :param profile_name:
        :return:
        """   
        text="?qualityProfile"
        combined=text+"="+profile_name

        # Make call (might raise exception) and return
        res = self._api._get_call(self.SEARCH_QUALITY_PROFILE_ENDPOINT, params=combined)
        return res if res.status_code == 204 else json.loads(res.content)

    def delete_quality_profile(self, profile_name, language):
        """

        :param profileName:
        :return:
        """

        data = {
            'profileName': profile_name,
            'language': language
        }

        # Make call (return nothing)
        self._api._make_call('post', self.DELETE_QUALITY_PROFILE_ENDPOINT, data)

    def create_quality_profile(self, key, name, language, languagename,
                               isinherited=False, isdefault=False, organization="default-organization"):
        """
        Create a quality profile

        :param key:
        :param name: name of the profile
        :param language: language used (java, C#...)
        :param languagename: language name (may be different from the language)
        :param isinherited: profile inherited
        :param isdefault: default rules
        :param organization:
        :return: request response
        """

        data = {
            'key': key,
            'name': name,
            'language': language,
            'languageName': languagename,
            'isInherited': isinherited,
            'isDefault': isdefault,
            'organization': organization
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.CREATE_QUALITY_PROFILE_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def add_project_to_quality_profile(self, profile_key, project_key):
        """
        Adds the project to the quality profile

        :param profile_key: key of the profile
        :param project_key: key of the project
        :return: request response
        """

        data = {
            'profileKey': profile_key,
            'projectKey': project_key
        }

        # Make call (might raise exception) and return no content
        self._api._make_call('post', self.ADD_PROJECT_TO_QUALITY_PROFILE_ENDPOINT, data=data)

    def activate_rule(self, key, profile_key, reset=False, severity=None,
                      **params):
        """
        Activate a rule for a given quality profile.

        :param key: key of the rule
        :param profile_key: key of the profile
        :param reset: reset severity and params to default
        :param severity: severity of rule for given profile
        :param params: customized parameters for the rule
        :return: request response
        """
        # Build main data to post
        data = {
            'rule_key': key,
            'profile_key': profile_key,
            'reset': reset and 'true' or 'false'
        }

        if not reset:
            # No reset, Add severity if given (if not default will be used?)
            if severity:
                data['severity'] = severity.upper()

            # Add params if we have any
            # Note: sort by key to allow checking easily
            params = ';'.join('{}={}'.format(k, v) for k, v in sorted(params.items()) if v)
            if params:
                data['params'] = params

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.RULES_ACTIVATION_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)
