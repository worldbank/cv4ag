'''
This class uses Requests, it may or may not work on App Engine.
See https://github.com/kennethreitz/requests/blob/master/requests/api.py
'''

import json
import urllib

import requests

from restwice.base_client import BaseClient
from restwice.enums import HttpMethod
from restwice.rest_exception import RestwiceException

DEFAULT_DEADLINE = 5  # To match URL fetch in AppEngine

class RequestsClient(BaseClient):

    def _get_uri_query(self, endpoint, data):
        # We need the endpoint + query params in GET requests in order to be
        # able to generate the OAuth1 signature
        request_raw = requests.Request(
            method=HttpMethod.GET, url=endpoint, params=data)
        prepared_request = request_raw.prepare()
        return prepared_request.url

    def _do_http_request(self, http_method, endpoint, data, headers, json_request, client_settings):
        # Defaults
        requests_params = None
        requests_data = None
        requests_json = None

        # Set the timeout
        requests_timeout = (
            client_settings.get('timeout') if 'timeout' in client_settings
            else DEFAULT_DEADLINE)

        # Add the data to right place
        if http_method in [HttpMethod.GET, HttpMethod.DELETE]:
            if isinstance(data, dict) and len(data) > 0:
                requests_params = data
        elif http_method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH]:
            # From what I gather, Requests automatically adds the corresponding
            # Content-Type header, so we don't need to manually add it.
            if isinstance(data, dict) and len(data) > 0:
                if json_request:
                    requests_json = data
                else:
                    requests_data = data
        elif http_method in [HttpMethod.OPTIONS, HttpMethod.HEAD]:
            # Also valid, anything we need to do here?
            pass
        else:
            raise RestwiceException('Unhandled Requests method: {}'.format(http_method))

        # Debug
        debug_dict = {
            'method': http_method.lower(),
            'url': endpoint,
            'params': requests_params,
            'data': requests_data,
            'json': requests_json,
            'headers': headers,
            'timeout': requests_timeout}
        print('[requests.request] %s' % json.dumps(debug_dict))

        # Fetch
        r = requests.request(
            method=http_method.lower(),
            url=endpoint,
            params=requests_params,
            data=requests_data,
            json=requests_json,
            headers=headers,
            timeout=requests_timeout)

        # Done
        return r.text, r.status_code
