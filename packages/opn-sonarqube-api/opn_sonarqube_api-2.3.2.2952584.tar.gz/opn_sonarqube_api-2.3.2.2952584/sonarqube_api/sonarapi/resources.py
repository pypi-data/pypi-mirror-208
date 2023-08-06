import json


import operator

class SonarAPIResources(object):
    RESOURCES_ENDPOINT = '/api/resources'

    # Debt data params (characteristics and metric)
    DEBT_CHARACTERISTICS = (
        'TESTABILITY', 'RELIABILITY', 'CHANGEABILITY', 'EFFICIENCY',
        'USABILITY', 'SECURITY', 'MAINTAINABILITY', 'PORTABILITY', 'REUSABILITY'
    )
    DEBT_METRICS = (
        'sqale_index',
    )

    # General metrics with their titles (not provided by api)
    GENERAL_METRICS = (
        # SQUALE metrics
        'sqale_index', 'sqale_debt_ratio',

        # Violations
        'violations', 'blocker_violations', 'critical_violations',
        'major_violations', 'minor_violations',

        # Coverage
        'lines_to_cover', 'conditions_to_cover', 'uncovered_lines',
        'uncovered_conditions', 'coverage'
    )

    def __init__(self, api=None):
        self._api = api

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
        # Build parameters
        params = {
            'model': 'SQALE', 'metrics': ','.join(self.DEBT_METRICS),
            'characteristics': ','.join(categories or self.DEBT_CHARACTERISTICS).upper()
        }
        if resource:
            params['resource'] = resource
        if include_trends:
            params['includetrends'] = 'true'
        if include_modules:
            params['qualifiers'] = 'TRK,BRC'

        # Get the results
        res = self._api._make_call('get', self.RESOURCES_ENDPOINT, **params).json()

        # Yield results
        for prj in res:
          yield prj

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
        # Build parameters
        params = {}
        if not metrics:
            metrics = self.GENERAL_METRICS
        if resource:
            params['resource'] = resource
        if include_trends:
            params['includetrends'] = 'true'
            metrics.extend(['new_{}'.format(m) for m in metrics])
        if include_modules:
            params['qualifiers'] = 'TRK,BRC'
        params['metrics'] = ','.join(metrics)

        # Make the call
        res = self._api._make_call('get', self.RESOURCES_ENDPOINT, **params).json()

        # Iterate and yield results
        for prj in res:
            yield prj

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
        # First make a dict with all resources
        prjs = {prj['key']: prj for prj in
                self.get_resources_metrics(
                    resource=resource, metrics=metrics,
                    include_trends=include_trends,
                    include_modules=include_modules
                )}

        # Now merge the debt data using the key
        for prj in self.get_resources_debt(
                resource=resource, categories=categories,
                include_trends=include_trends,
                include_modules=include_modules
        ):
            if prj['key'] in prjs:
                prjs[prj['key']]['msr'].extend(prj['msr'])
            else:
                prjs[prj['key']] = prj

        # Now yield all values
        for _, prj in sorted(prjs.items(), key=operator.itemgetter(0)):
            yield prj