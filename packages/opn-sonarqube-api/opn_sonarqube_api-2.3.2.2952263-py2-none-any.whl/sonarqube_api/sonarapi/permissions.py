import json


class SonarAPIPermissionTemplates(object):
    #Endpoint for permission templates
    PERMISSIONS_TEMPLATE_CREATE_ENDPOINT = '/api/permissions/create_template'
    PERMISSIONS_TEMPLATE_LIST_ENDPOINT = '/api/permissions/search_templates'
    PERMISSIONS_TEMPLATE_DELETE_ENDPOINT = '/api/permissions/delete_template'
    PERMISSIONS_TEMPLATE_UPDATE_ENDPOINT = '/api/permissions/update_template'
    PERMISSIONS_TEMPLATE_GROUPS = '/api/permissions/template_groups'
    PERMISSIONS_TEMPLATE_ADD_GROUP = '/api/permissions/add_group_to_template'
    PERMISSIONS_TEMPLATE_REMOVE_GROUP = '/api/permissions/remove_group_from_template'
    PERMISSIONS_ADD_USER = '/api/permissions/add_user'
    PERMISSIONS_REMOVE_USER = '/api/permissions/remove_user'
    PERMISSIONS_SEARCH_USER = '/api/permissions/users'
    PERMISSIONS_ADD_GROUP = '/api/permissions/add_group'
    PERMISSIONS_REMOVE_GROUP = '/api/permissions/remove_group'
    PERMISSIONS_SEARCH_GROUP = '/api/permissions/groups'

    permissions = ['user', 'codeviewer', 'issueadmin', 'admin', 'scan']
    global_permissions = ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']


    def __init__(self, api=None):
        self._api = api

    def create_template(self, template_name, template_description, project_key_pattern):
        """
        Create template.

        :param template_name: name of the template
        :param template_description: description of the template
        :param projectKeyPattern: Pattern for the template template
        :return: request response
        """
        # Build main data to post
        data = {
            'name': template_name,
            'description': template_description,
            'projectKeyPattern': project_key_pattern
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_TEMPLATE_CREATE_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def search_template(self, template_name):
        """
        Search template with specified name.

        :param template_name: name of the group
        :return: request response
        """
        # Build main data to post
        data = {
            'q': template_name
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('get', self.PERMISSIONS_TEMPLATE_LIST_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def delete_template(self, template_id):
        """
        Delete template id.

        :param template_id: id of the template to delete
        :return: request response
        """
        # Build main data to post
        data = {
            'templateId': template_id
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_TEMPLATE_DELETE_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def update_template(self, template_id, template_name, template_description, project_key_pattern):
        """
        update permission template.

        :param template_id: id of the template to update
        :param template_name: new name
        :param template_description: new description
        :param template_description: new description
        :return: request response
        """
        # Build main data to post
        data = {
            'id': template_id,
            'name': template_name,
            'description': template_description,
            'projectKeyPattern': project_key_pattern
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_TEMPLATE_UPDATE_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def list_groups_of_template(self, template_id):
        """
        get permission template's groups.

        :param template_id: id of the template to update
        :return: request response
        """
        # Build main data to get
        text="?templateId"
        combined=text+"="+template_id

        # Make call (might raise exception) and return
        res = self._api._get_call(self.PERMISSIONS_TEMPLATE_GROUPS, params=combined)
        return res if res.status_code == 204 else json.loads(res.content)

    def add_group_to_template(self, template_id, group_name, permission):
        """
        update permission template.

        :param template_id: id of the template to update
        :param group_name: name of the group to associate
        :param permission: permission to set in ['user', 'codeviewer', 'issueadmin', 'admin', 'scan']
        :return: request response
        """
        # Build main data to post
        data = {
            'templateId': template_id,
            'groupName': group_name,
            'permission': permission
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_TEMPLATE_ADD_GROUP, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def remove_group_from_template(self, template_id, group_name, permission):
        """
        update permission template.

        :param template_id: id of the template to update
        :param group_name: name of the group to associate
        :param permission: permission to unset in ['user', 'codeviewer', 'issueadmin', 'admin', 'scan']
        :return: request response
        """
        # Build main data to post
        data = {
            'templateId': template_id,
            'groupName': group_name,
            'permission': permission
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_TEMPLATE_REMOVE_GROUP, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def add_permission_to_user(self, user_name, permission):
        """
        update user's permission.

        :param user_name: name of the group to associate
        :param permission: permission to set in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        # Build main data to post
        data = {
            'login': user_name,
            'permission': permission
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_ADD_USER, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def remove_permission_to_user(self, user_name, permission):
        """
        update user's permission.

        :param user_name: name of the group to associate
        :param permission: permission to remove in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        # Build main data to post
        data = {
            'login': user_name,
            'permission': permission
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_REMOVE_USER, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def search_permission_for_user(self, user_name):
        """
        list user permission.

        :param user_name: name of the user to search
        :return: request response
        """
        # Build main data to post
        data = {
            'q': user_name,
            'ps': 100
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('get', self.PERMISSIONS_SEARCH_USER, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def add_permission_to_group(self, group_name, permission):
        """
        update group's permission.

        :param group_name: name of the group to associate
        :param permission: permission to set in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        # Build main data to post
        data = {
            'groupName': group_name,
            'permission': permission
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_ADD_GROUP, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def remove_permission_to_group(self, group_name, permission):
        """
        update group's permission.

        :param group_name: name of the group to associate
        :param permission: permission to remove in ['admin', 'gateadmin', 'profileadmin', 'scan', 'provisioning']
        :return: request response
        """
        # Build main data to post
        data = {
            'groupName': group_name,
            'permission': permission
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.PERMISSIONS_REMOVE_GROUP, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

    def search_permission_for_group(self, group_name):
        """
        list groups permission.

        :param group_name: name of the group to associate
        :return: request response
        """
        # Build main data to get
        text="?ps=100&q"
        combined=text+"="+group_name

        # Make call (might raise exception) and return
        res = self._api._get_call(self.PERMISSIONS_SEARCH_GROUP, params=combined)
        return res if res.status_code == 204 else json.loads(res.content)
