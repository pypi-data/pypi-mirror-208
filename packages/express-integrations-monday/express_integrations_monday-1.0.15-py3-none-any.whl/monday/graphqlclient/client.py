import time

import requests

import backoff


def fatal_code(e) -> bool:
    return 400 <= e.response.status_code < 500


class GraphQLClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = None
        self.header_name = None

    def execute(self, query, variables=None):
        query_type = 'query' if 'query' in query else 'mutation'
        stripped_query = query.strip().lstrip(f"{query_type} {{")
        query_with_complexity = f"""{query_type} {{
          complexity {{
            reset_in_x_seconds,
            after,
            before,
            query
          }}
          {stripped_query}
        """
        r = self._send(query_with_complexity, variables)
        if 'errors' in r:
            print(f"Query with Complexity: {query_with_complexity}")
            raise requests.HTTPError(', '.join([e['message'] if 'message' in e else str(e) for e in r['errors']]))

        # rate limiting
        complexity = r['data']['complexity']
        while complexity['before'] - complexity['query'] < 0:
            time.sleep(complexity['reset_in_x_seconds'] + 1)
            r = self._send(query_with_complexity, variables)
            complexity = r['data']['complexity']
        if 'errors' in r:
            print(f"Query with Complexity: {query_with_complexity}")
            raise requests.HTTPError(', '.join([e['message'] if 'message' in e else str(e) for e in r['errors']]))
        return r['data']

    def inject_token(self, token, header_name='Authorization'):
        self.token = token
        self.header_name = header_name

    # noinspection PyTypeChecker
    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries = 8,
        raise_on_giveup = True,
        giveup = fatal_code
    )
    def _send(self, query, variables):
        payload = {'query': query}
        headers = {}
        files = None

        if self.token is not None:
            headers[self.header_name] = '{}'.format(self.token)

        if variables is None:
            headers['Content-Type'] = 'application/json'
        elif variables.get('file', None) is not None:
            headers['content'] = 'multipart/form-data'
            files = [
                ('variables[file]', (variables['file'], open(variables['file'], 'rb')))
            ]

        response = requests.post(url=self.endpoint, headers=headers, json=payload, files=files)
        if not response.ok:
            print(f"Original payload: {payload}")
            print(response.text)
            response.raise_for_status()
        return response.json()
