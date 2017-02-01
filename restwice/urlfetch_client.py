'''
This class will only work on App Engine because it uses urlfetch.
'''

import json
import urllib

from google.appengine.api import urlfetch

from restwice.base_client import BaseClient
from restwice.enums import HttpMethod
from restwice.rest_exception import RestwiceException

import logging

# Limits:
# * Request size: 10 megabytes
# * Response size: 32 megabytes
# * Maximum deadline (request handler): 60 seconds
# * Maximum deadline (task queue and cron job handler): 10 minutes

DEFAULT_DEADLINE = 5  # Default from AppEngine


class UrlFetchClient(BaseClient):

    def _get_uri_query(self, endpoint, data):
        # We need the endpoint + query params in GET requests in order to be
        # able to generate the OAuth1 signature
        return '{}?{}'.format(endpoint, urllib.urlencode(data))

    def _do_http_request(self, http_method, endpoint, data, headers, json_request, client_settings):
        # Defaults
        urlfetch_url = endpoint
        urlfetch_payload = None
        urlfetch_method = http_method
        urlfetch_headers = headers if isinstance(headers, dict) else {}

        # Set the deadline
        urlfetch_deadline = (
            client_settings.get('deadline') if 'deadline' in client_settings
            else DEFAULT_DEADLINE)

        # Set the data in the right place nd format
        if http_method in [HttpMethod.GET, HttpMethod.DELETE]:
            if isinstance(data, dict) and len(data) > 0:
                urlfetch_url = self._get_uri_query(endpoint=endpoint, data=data)
        elif http_method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH]:
            if isinstance(data, dict) and len(data) > 0:
                if json_request:
                    urlfetch_payload = json.dumps(data)
                    urlfetch_headers['Content-Type'] = 'application/json'
                else:
                    urlfetch_payload = urllib.urlencode(data)
                    urlfetch_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif http_method in [HttpMethod.HEAD]:
            # Also valid, anything we need to do here?
            pass
        else:
            raise RestwiceException('Invalid urlfetch method: {}'.format(http_method))

        # Debug
        debug_dict = {
            'url': urlfetch_url,
            'payload': urlfetch_payload,
            'method': urlfetch_method,
            'headers': urlfetch_headers,
            'deadline': urlfetch_deadline}
        logging.info('[urlfetch.fetch] %s' % json.dumps(debug_dict))

        # Do the actual request
        result = urlfetch.fetch(
            url=urlfetch_url, payload=urlfetch_payload, method=urlfetch_method,
            headers=urlfetch_headers, deadline=urlfetch_deadline)

        # Done
        return result.content, result.status_code
