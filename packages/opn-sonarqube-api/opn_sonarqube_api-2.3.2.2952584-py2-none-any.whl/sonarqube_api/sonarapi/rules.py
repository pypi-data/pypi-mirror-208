import json


class SonarAPIRules(object):
    # Endpoint for rules
    RULES_LIST_ENDPOINT = '/api/rules/search'
    RULES_CREATE_ENDPOINT = '/api/rules/create'

    def __init__(self, api=None):
        self._api = api


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
        # Build data to post
        data = {
            'custom_key': key,
            'name': name,
            'markdown_description': description,
            'params': 'message={};xpathQuery={}'.format(message, xpath),
            'severity': severity.upper(),
            'status': status.upper(),
            'template_key': template_key
        }

        # Make call (might raise exception) and return
        res = self._api._make_call('post', self.RULES_CREATE_ENDPOINT, data=data)
        return res if res.status_code == 204 else json.loads(res.content)

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
        # Build the queryset
        qs = {'is_template': 'no', 'statuses': 'READY'}

        # Add profile and activity params
        if profile:
            qs.update({'activation': 'true', 'qprofile': profile})
        elif active_only:
            qs['activation'] = 'true'

        # Add language param
        # Note: we handle comma-separated string or list-like iterable)
        if languages:
            if not isinstance(languages, str):
                languages = ','.join(languages)
            qs['languages'] = languages.lower()

        # Filter by tech debt for custom only (custom have no tech debt)
        if custom_only:
            qs['has_debt_characteristic'] = 'false'

        # Page counters
        page_num = 1
        page_size = 1
        n_rules = 2

        # Cycle through rules
        while page_num * page_size < n_rules:
            # Update paging information for calculation
            res = self._api._make_call('get', self.RULES_LIST_ENDPOINT, **qs).json()
            page_num = res['p']
            page_size = res['ps']
            n_rules = res['total']

            # Update page number (next) in queryset
            qs['p'] = page_num + 1

            # Yield rules
            for rule in res['rules']:
                yield rule
