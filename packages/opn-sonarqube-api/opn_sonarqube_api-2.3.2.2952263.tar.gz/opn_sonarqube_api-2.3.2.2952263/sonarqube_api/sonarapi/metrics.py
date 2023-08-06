import json


class SonarAPIMetrics(object):
    # Endpoint for resources and rules
    METRICS_LIST_ENDPOINT = '/api/metrics/search'

    def __init__(self, api=None):
        self._api = api

    def get_metrics(self, fields=None):
        """
        Yield defined metrics.

        :param fields: iterable or comma-separated string of field names
        :return: generator that yields metric data dicts
        """
        # Build queryset including fields if required
        qs = {}
        if fields:
            if not isinstance(fields, str):
                fields = ','.join(fields)
            qs['f'] = fields.lower()

        # Page counters
        page_num = 1
        page_size = 1
        n_metrics = 2

        # Cycle through rules
        while page_num * page_size < n_metrics:
            # Update paging information for calculation
            res = self._api._make_call('get', self.METRICS_LIST_ENDPOINT,
                                  **qs).json()
            page_num = res['p']
            page_size = res['ps']
            n_metrics = res['total']

            # Update page number (next) in queryset
            qs['p'] = page_num + 1

            # Yield rules
            for metric in res['metrics']:
                yield metric