'''
Base class for all clients
'''

import hashlib
import json

# Required by the get_oauth1_signature() method
try:
    from oauthlib import oauth1
except ImportError:
    oauth1 = None

from restwice.enums import HttpMethod, HttpStatusCode
from restwice.rest_exception import RestwiceException

DEFAULT_MEMCACHE_TIME = 24 * 60 * 60  # 1 day
DEFAULT_MEMCACHE_NAMESPACE = 'restwice'


class BaseClient(object):
    def __init__(self):
        # Defaults
        self._endpoint = ''
        self._data = {}
        self._headers = {}

        # Default memcache settings
        self._memcache_client = None
        self._memcache_enabled = False
        self._memcache_time = DEFAULT_MEMCACHE_TIME
        self._memcache_namespace = DEFAULT_MEMCACHE_NAMESPACE

    def set_endpoint(self, endpoint):
        self._endpoint = endpoint

    def set_data(self, data):
        self._data = data

    def set_headers(self, headers):
        self._headers.update(headers)

    def enable_cache(self, memcache_client, memcache_time=None, memcache_namespace=None):
        if memcache_client is not None:
            self._memcache_client = memcache_client
            self._memcache_enabled = True
        if memcache_time is not None:
            self._memcache_time = memcache_time
        if memcache_namespace is not None:
            self._memcache_namespace = memcache_namespace

    def disable_cache(self):
        self._memcache_enabled = False

    '''
    CRUD methods.

    Param `client_settings` includes specific settings for the actual client.
    For example, if we wanted to change the `deadline` for urlfetch.fetch() we
    could add client_settings={'deadline': 60}.
    '''

    def do_get(self, json_response=True, json_request=True, with_cache=True, client_settings={}):
        return self.do_request(
            http_method=HttpMethod.GET, json_response=json_response,
            json_request=json_request, with_cache=with_cache,
            client_settings=client_settings)

    def do_post(self, json_response=True, json_request=True, with_cache=False, client_settings={}):
        return self.do_request(
            http_method=HttpMethod.POST, json_response=json_response,
            json_request=json_request, with_cache=with_cache,
            client_settings=client_settings)

    def do_put(self, json_response=True, json_request=True, with_cache=False, client_settings={}):
        return self.do_request(
            http_method=HttpMethod.PUT, json_response=json_response,
            json_request=json_request, with_cache=with_cache,
            client_settings=client_settings)

    def do_delete(self, json_response=True, json_request=True, with_cache=False, client_settings={}):
        return self.do_request(
            http_method=HttpMethod.DELETE, json_response=json_response,
            json_request=json_request, with_cache=with_cache,
            client_settings=client_settings)

    '''
    Signs the current request using OAuth1.

    *Make sure* you set the values for self._endpoint, self._data, and
    self._headers before signing the request. We're using the SIGNATURE_HMAC
    method. The resulting authentication goes in in an Authorization header.

    We originally added this for Factual. See:
    * http://developer.factual.com/throttling-limits/ (docs)
    * https://github.com/Factual/factual-python-driver/blob/master/factual/api.py (see _generate_token)
    * https://github.com/requests/requests-oauthlib/blob/master/requests_oauthlib/oauth1_auth.py
    * https://github.com/idan/oauthlib/blob/master/oauthlib/oauth1/rfc5849/__init__.py (see Client.sign)
    '''

    def oauth1_sign_headers(self, client_key, client_secret, http_method):
        # Check lib is ready
        if oauth1 is None:
            raise RestwiceException(
                'You need to install the oauthlib package '
                'in order to use this method.')

        # Client is ready
        client = oauth1.Client(
            client_key=client_key,
            client_secret=client_secret,
            signature_method=oauth1.SIGNATURE_HMAC,
            signature_type=oauth1.SIGNATURE_TYPE_AUTH_HEADER)

        # For GET requests, the body must be empty
        if http_method == HttpMethod.GET:
            uri = self._get_uri_query(endpoint=self._endpoint, data=self._data)
            body = None
        elif http_method == HttpMethod.POST:
            uri = self._endpoint
            body = self._data
            self._headers['Content-Type'] = 'application/x-www-form-urlencoded'
        else:
            raise RestwiceException(
                'For now, I only know how to handle GET and POST requests.')

        # Get signature
        uri_signed, headers_signed, body_signed = client.sign(
            uri=uri,
            http_method=http_method,
            body=body,
            headers=self._headers)

        # Because we're including the authorization in the header, we don't
        # need to change the URI or the body (as they remain the same). We
        # just need to update the request headers
        self._headers = headers_signed

    '''
    Caching logic
    '''

    def get_memcache_key(self, http_method):
        # We consider that requests are the same, when they share the same
        # HTTP method, endpoint, data, and headers.
        pieces = []
        pieces.append('http_method:{}'.format(http_method))
        pieces.append('endpoint:{}'.format(self._endpoint))
        for key, value in self._data.items():
            pieces.append('data:{}:{}'.format(key, value))
        for key, value in self._headers.items():
            # We don't include the Authorization header because in some cases
            # it changes with equivalent requests (the oauthlib case above).
            if key != 'Authorization':
                pieces.append('header:{}:{}'.format(key, value))

        # Because dicts are not sorted, we sort our list to make sure we
        # don't detect as different requests that are equal but came in 
        # different order
        sorted_pieces = sorted(pieces)

        # Implode the list, and compute a hash
        key = hashlib.md5('|'.join(sorted_pieces)).hexdigest()
        return key

    def get_memcache_count_key(self):
        # See memcache_increment() below
        return '{}_count'.format(self._memcache_namespace)

    def get_memcache_count_value(self):
        # Returns 0 if nothing found
        count_key = self.get_memcache_count_key()
        count = self.memcache_get(key=count_key)
        return count or 0

    def reset_memcache_count_key(self):
        count_key = self.get_memcache_count_key()
        self._memcache_client.set(
            key=count_key,
            value=0,
            namespace=self._memcache_namespace)

    def memcache_set(self, key, value):
        # The return value is True if set, False on error.
        return self._memcache_client.set(
            key=key, value=value,
            time=self._memcache_time, namespace=self._memcache_namespace)

    def memcache_get(self, key):
        # The return value is the value of the key, if found in memcache, else None.
        return self._memcache_client.get(
            key=key, namespace=self._memcache_namespace)

    def memcache_increment(self):
        # Counts the actual requests under this namespace. The return value is
        # a new long integer value, or None if key was not in the cache or
        # could not be incremented for any other reason.
        # NOTE that the client does *not* reset the counter, it's up to the app
        # to set a cron job to read/reset the ocunter at the time it prefers
        # using get_memcache_count_key() to get the correspoding key value.
        count_key = self.get_memcache_count_key()
        return self._memcache_client.incr(
            key=count_key, delta=1, namespace=self._memcache_namespace, initial_value=1)

    '''
    Generic request
    It returns the result (parsed if requested) and a cached_result boolean.
    '''

    def do_request(
            self, http_method=HttpMethod.GET, json_response=True,
            json_request=True, with_cache=False, client_settings={}):
        # Defaults
        raw_result = None
        status_code = None
        memcache_key = None
        cached_result = False

        # Check chache, if applies
        if with_cache and self._memcache_enabled:
            memcache_key = self.get_memcache_key(http_method=http_method)
            raw_result = self.memcache_get(key=memcache_key)
            if raw_result is not None:
                status_code = HttpStatusCode.OK
                cached_result = True

        # Do the actual request if necessary
        if raw_result is None:
            raw_result, status_code = self._do_http_request(
                http_method=http_method, endpoint=self._endpoint,
                data=self._data, headers=self._headers, json_request=json_request,
                client_settings=client_settings)
            if self._memcache_enabled:
                self.memcache_increment()

        # Update the cache
        if (with_cache and self._memcache_enabled and raw_result is not None and not cached_result):
            self.memcache_set(key=memcache_key, value=raw_result)

        # Parse result if requested
        if json_response and raw_result is not None:
            try:
                result = json.loads(raw_result)
            except:
                print 'JSON decoding failed, raw response was: %s' % raw_result
                raise
            else:
                return result, cached_result

        # Done
        return raw_result, cached_result

    '''
    These are the methods that need to be implemented by the specific client.
    do_http_request() returns a raw_result, and a status_code.
    '''

    def _get_uri_query(self, endpoint, data):
        # We need the endpoint + query params in GET requests in order to be
        # able to generate the OAuth1 signature (see oauth1_sign_headers above)
        raise NotImplementedError('BaseClient: _get_uri_query() not implemented.')

    def _do_http_request(self, http_method, endpoint, data, headers, json_request, client_settings):
        raise NotImplementedError('BaseClient: _do_http_request() not implemented.')
