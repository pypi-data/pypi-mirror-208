"""
This module contains the SonarAPIHandler, used for communicating with the
SonarQube server web service API.
"""

from .api import SonarAPIHandler
from .sonarapi.authentication import SonarAPIAuthentication
from .sonarapi.groups import SonarAPIGroup
from .sonarapi.metrics import SonarAPIMetrics
from .sonarapi.permissions import SonarAPIPermissionTemplates
from .sonarapi.qualitygates import SonarAPIQGates
from .sonarapi.qualityprofiles import SonarAPIQualityProfile
from .sonarapi.resources import SonarAPIResources
from .sonarapi.rules import SonarAPIRules
from .sonarapi.settings import SonarAPISettings
from .sonarapi.user_token import SonarAPIUserToken
from .sonarapi.users import SonarAPIUser
from .sonarapi.components import SonarAPIComponents
from .sonarapi.projects import SonarAPIProjects
from .sonarapi.branches import SonarAPIBranches


class SonarAPI(object):
    """
    Adapter for SonarQube's web service API.
    """
    # Default host is local
    DEFAULT_HOST = 'http://localhost'
    DEFAULT_PORT = 9000
    DEFAULT_BASE_PATH = ''

    def __init__(self, host=None, port=None, user=None, password=None,
                 base_path=None, token=None, headers=None):

        self.api = SonarAPIHandler(host=host or self.DEFAULT_HOST, port=port or self.DEFAULT_PORT, user=user, password=password,
                                   base_path=base_path or self.DEFAULT_BASE_PATH, token=token, headers=headers)
        self._group = SonarAPIGroup(api=self.api)
        self._permissions = SonarAPIPermissionTemplates(api=self.api)
        self._user_token = SonarAPIUserToken(api=self.api)
        self._user = SonarAPIUser(api=self.api)
        self._metrics = SonarAPIMetrics(api=self.api)
        self._qualityprofile = SonarAPIQualityProfile(api=self.api)
        self._resources = SonarAPIResources(api=self.api)
        self._rules = SonarAPIRules(api=self.api)
        self._settings = SonarAPISettings(api=self.api)
        self._qgates = SonarAPIQGates(api=self.api)
        self._authentication = SonarAPIAuthentication(api=self.api)
        self._components = SonarAPIComponents(api=self.api)
        self._projects = SonarAPIProjects(api=self.api)
        self._branches = SonarAPIBranches(api=self.api)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # #
    # #  API
    # #

    def get_url(self, endpoint):
        return self.api.get_url(endpoint)

    def validate_authentication(self):
        return self._authentication.validate_authentication()

    # user group API
    def create_group(self, group_name, group_description):
        return self._group.create_group(group_name, group_description)

    def search_group(self, group_name):
        return self._group.search_group(group_name)

    def update_group(self, group_id, group_name, group_description):
        return self._group.update_group(group_id, group_name, group_description)

    def delete_group(self, group_id):
        return self._group.delete_group(group_id)

    # permissions API
    def create_permission_template(self, template_name, template_description, project_key_pattern):
        return self._permissions.create_template(template_name, template_description, project_key_pattern)

    def update_permission_template(self, template_id, template_name, template_description, project_key_pattern):
        return self._permissions.update_template(template_id, template_name, template_description, project_key_pattern)

    def search_permission_template(self, template_name):
        return self._permissions.search_template(template_name)

    def delete_permission_template(self, template_id):
        return self._permissions.delete_template(template_id)

    def add_group_to_template(self, template_id, group_name, permission):
        return self._permissions.add_group_to_template(template_id, group_name, permission)

    def list_groups_of_template(self, template_id):
        return self._permissions.list_groups_of_template(template_id)

    def remove_group_from_template(self, template_id, group_name, permission):
        return self._permissions.remove_group_from_template(template_id, group_name, permission)

    def add_permission_to_user(self, user_name, permission):
        """
        update user's permission.

        :param user_name: name of the group to associate
        :param permission: permission to set in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        return self._permissions.add_permission_to_user(user_name, permission)

    def remove_permission_to_user(self, user_name, permission):
        """
        update user's permission.

        :param user_name: name of the group to associate
        :param permission: permission to remove in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        return self._permissions.remove_permission_to_user(user_name, permission)

    def add_permission_to_group(self, group_name, permission):
        """
        update groups permission.

        :param group_name: name of the group to associate
        :param permission: permission to set in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        return self._permissions.add_permission_to_group(group_name, permission)

    def remove_permission_to_group(self, group_name, permission):
        """
        update groups permission.

        :param group_name: name of the group to associate
        :param permission: permission to remove in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        return self._permissions.remove_permission_to_group(group_name, permission)

    def search_permission_for_group(self, group_name):
        """
        list groups permission.

        :param group_name: name of the group to associate
        :return: request response
        """
        return self._permissions.search_permission_for_group(group_name)

    # user token
    def generate_token(self, token_name, user_login):
        """
        Create user token.

        :param token_name: name of the token to generate
        :param user_login: user to generate token for
        :return: request response
        """
        return self._user_token.generate_token(token_name, user_login)

    def revoke_token(self, token_name, user_login):
        """
        Revoke user token.

        :param token_name: name of the token to revoke
        :param user_login: user to generate token for
        :return: request response
        """
        return self._user_token.revoke_token(token_name, user_login)

    def user_tokens(self, user_login):
        """
        List existing token for user.
        :param user_login: user to generate token for
        """
        return self._user_token.search_token(user_login)

    # user
    def user_current(self):
        return self._user.current()

    # metrics
    def get_metrics(self, fields=None):
        """
        Yield defined metrics.

        :param fields: iterable or comma-separated string of field names
        :return: generator that yields metric data dicts
        """
        return self._metrics.get_metrics(fields)

    # quality profile
    def project_quality_profile(self, key, query, ps=50, selected='all'):
        """
        get projets list.

        :param key: Id of the qualityprofile
        :param query: query to send
        :param ps: pageSize
        :param selected: all/selected/deselected
        :return: request response
        """
        return self._qualityprofile.project(key=key, query=query, ps=ps, selected=selected)

    def restore_quality_profile_from_xml(self, backup, project_name):
        """
        Create a quality profile with rules from a xml file

        :param backup:
        :return:
        """
        return self._qualityprofile.restore_quality_profile_from_xml(backup, project_name)

    # quality profile
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
        return self._qualityprofile.create_quality_profile(key, name, language, languagename,
                                                           isinherited, isdefault, organization)

    # quality profile
    def add_project_to_quality_profile(self, profile_key, project_key):
        """
        Adds the project to the quality profile

        :param profile_key: key of the profile
        :param project_key: key of the project
        :return: no content
        """
        self._qualityprofile.add_project_to_quality_profile(profile_key, project_key)

    # quality profile
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
        return self._qualityprofile.activate_rule(key, profile_key, reset, severity, **params)

    def delete_quality_profile(self, profile_name, language):
        return self._qualityprofile.delete_quality_profile(profile_name, language)

    # resources
    def get_resources_debt(self, resource=None, categories=None,
                           include_trends=False, include_modules=False):
        """
        Yield first-level resources with debt by category (aka. characteristic).

        :param resource: key of the resource to select
        :param categories: iterable of debt characteristics by name
        :param include_trends: include differential values for leak periods
        :param include_modules: include modules data
        :return: generator that yields resource debt data dicts
        """
        return self._resources.get_resources_debt(resource, categories,
                                                  include_trends, include_modules)

    def get_resources_metrics(self, resource=None, metrics=None,
                              include_trends=False, include_modules=False):
        """
        Yield first-level resources with generic metrics.

        :param resource: key of the resource to select
        :param metrics: iterable of metrics to return by name
        :param include_trends: include differential values for leak periods
        :param include_modules: include modules data
        :return: generator that yields resource metrics data dicts
        """
        return self._resources.get_resources_metrics(resource, metrics,
                                                     include_trends, include_modules)

    # rules
    def create_rule(self, key, name, description, message, xpath, severity,
                    status, template_key):
        """
        Create a a custom rule.

        :param key: key of the rule to create
        :param name: name of the rule
        :param description: markdown description of the rule
        :param message: issue message (title) for the rule
        :param xpath: xpath query to select the violation code
        :param severity: default severity for the rule
        :param status: status of the rule
        :param template_key: key of the template from which rule is created
        :return: request response
        """
        return self._rules.create_rule(key, name, description, message, xpath, severity,
                                       status, template_key)

    def get_rules(self, active_only=False, profile=None, languages=None,
                  custom_only=False):
        """
        Yield rules in status ready, that are not template rules.

        :param active_only: filter only active rules
        :param profile: key of profile to filter rules
        :param languages: key of languages to filter rules
        :param custom_only: filter only custom rules
        :return: generator that yields rule data dicts
        """
        return self._rules.get_rules(active_only, profile, languages,
                                     custom_only)

    def get_resources_full_data(self, resource=None, metrics=None,
                                categories=None, include_trends=False,
                                include_modules=False):
        """
        Yield first-level resources with merged generic and debt metrics.

        :param resource: key of the resource to select
        :param metrics: iterable of metrics to return by name
        :param categories: iterable of debt characteristics by name
        :param include_trends: include differential values for leak periods
        :param include_modules: include modules data
        :return: generator that yields resource metrics and debt data dicts
        """
        return self._resources.get_resources_full_data(resource, metrics,
                                                       categories, include_trends,
                                                       include_modules)

    def setting(self, key, value):
        """
        Create/update setting.

        :param key: name of the setting to update
        :param value: value to set
        :return: request response
        """
        return self._settings.set(key, value)

    def getting(self, key):
        """
        Create/update setting.

        :param key: name of the setting to get
        :return: request response
        """
        return self._settings.get(key)

    def list_qualitygates(self):
        """
        list quality gates.

        :return: request response
        """
        return self._qgates.list()

    def show_qualitygates(self, id=None, name=None):
        """
        get quality gate details, using id or name (id is prior is both are set)

        :param id: id of the quality gate
        :param name: name of the quality gate
        :return: request response
        """
        return self._qgates.show(id=id, name=name)

    def create_qualitygates(self, name):
        """
        create a new empty quality agte

        :param name: name of the quality gate
        :return: request response
        """
        return self._qgates.create(name)

    def destroy_qualitygates(self, id):
        """
        delete a quality agte

        :param id: id of the quality gate
        :return: request response
        """
        return self._qgates.destroy(id)

    def select_qualitygates(self, gateId, projectId):
        """
        assign a quality gate to a project

        :param gateId: id of the quality gate
        :param projectid: id of the project
        :return: 204 no content
        """
        return self._qgates.select(gateId=gateId, projectId=projectId)

    def search_project_qualitygates(self, gateId, query, ps=50, selected='all'):
        """
        get projets list.

        :param gateId: Id of the qualitygate
        :param query: query to send
        :param ps: pageSize
        :param selected: all/selected/deselected
        :return: request response
        """
        return self._qgates.search_project(gateId, query, ps, selected)

    def qg_get_for_project(self, project, organization='default-organization'):
        """
        get qg summary for a project

        :param project: project to use
        :param organization: organization or 'default-organization'
        :return: request response
        """
        return self._qgates.get_for_project(project, organization)

    def create_condition_qualitygates(self, gateid, metric, op, error):
        """
        create a condition for a quality gate

        :param gateid: id of the quality gate
        :param metric: metric of the condition
        :param op: operator of the condition
        :param error: value of the condition
        :return: request response
        """
        return self._qgates.create_condition(gateid, metric, op, error)

    def create_quality_gate_from_json(self, data, project_name):
        """
        create quality gate and conditions with json information

        :param data: json information

        :return: request response
        """
        return self._qgates.create_quality_gate_from_json(data, project_name)

    def delete_condition_qualitygates(self, id):
        """
        delete a condition in quality gate

        :param id: id of the condition gate
        :return: request response
        """
        return self._qgates.delete_condition(id)

    def update_condition_qualitygates(self, id, metric, op, error):
        """
        update a condition for a quality gate

        :param id: id of the condition
        :param metric: metric of the condition
        :param op: operator of the condition
        :param error: value of the condition
        :return: request response
        """
        return self._qgates.update_condition(id, metric, op, error)

    def search_project_components(self, query, ps=50, facets=None, f=None):
        """
        get projets list.

        :param query: query to send
        :return: request response
        """
        return self._components.search_project(query, ps, facets, f)

    def search_projects(self, query):
        """
        search project

        :param query: Limit search to:
            component names that contain the supplied string
            component keys that contain the supplied string
        :return: request response
        """
        return self._projects.search(query)

    def branches_list(self, project):
        """
        get project branches

        :param project: List the branches of a project.
        :return: request response
        """
        return self._branches.get(project)
