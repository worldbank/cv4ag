'''
This is a simple memcache (almost mock) object that stores the results in the
filesystem (as a raw plain text response). This is useful during development
to keep a local copy of the responses, and to accelerate them if the server
is slow or limits our requests.

Usage:

    memcache_client = MemcacheLocal(root_folder='_cache')
    rest_client.enable_cache(
        memcache_client=memcache_client,
        memcache_namespace=MEMCACHE_NAMESPACE)

We only implement a subset from this API:
https://cloud.google.com/appengine/docs/python/memcache/clientclass
'''

import os
import json

DEFAULT_ENCODING = 'utf-8'


class MemcacheLocal(object):
    def __init__(self, extension='json', root_folder=None):
        self._extension = extension
        self._root_folder = root_folder or '/tmp'
        if not os.path.isdir(self._root_folder):
            try:
                os.mkdir(self._root_folder)
                print '[memcachelocal] Root folder created: %s' \
                    % self._root_folder
            except Exception as e:
                print '[memcachelocal] Failed to create the root folder \
                    (%s): %s' % (self._root_folder, unicode(e))

    '''
    API
    '''

    def get(self, key, namespace=None, for_cas=False):
        # Param for_cas is ignored
        filepath = self._get_filepath(namespace=namespace, key=key)
        return self._get_content(filepath=filepath)

    def set(self, key, value, time=0, min_compress_len=0, namespace=None):
        # Params time and min_compress_len are ignored
        filepath = self._get_filepath(namespace=namespace, key=key)
        return self._set_content(filepath=filepath, content=value)

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        filepath = self._get_filepath(namespace=namespace, key='incr')
        content = self._get_content(filepath=filepath)
        content_decoded = {} if content is None else json.loads(content)
        content_decoded[key] = (content_decoded[key] + delta) \
            if key in content_decoded else initial_value
        content_encoded = json.dumps(content_decoded, indent=2)
        self._set_content(filepath=filepath, content=content_encoded)
        return content_decoded[key]

    '''
    Internal methods
    '''

    def _get_filepath(self, namespace, key):
        prefix = namespace or 'restwice'
        filename = '%s_%s.%s' % (prefix, key, self._extension)
        return os.path.join(self._root_folder, filename)

    def _get_content(self, filepath):
        if not os.path.isfile(filepath):
            print '[memcachelocal] This request hasn\'t been cached yet (%s).' \
                % filepath
            return None
        try:
            f = open(filepath, 'r')
            content = f.read().decode(DEFAULT_ENCODING)
            f.close()
        except Exception as e:
            print '[memcachelocal] Failed to read cache file (%s): %s' % \
                (filepath, unicode(e))
            return None
        else:
            return content

    def _set_content(self, filepath, content):
        if content is None or len(content) == 0:
            print '[memcachelocal] Got no content (%s), ignoring.' % filepath
            return
        try:
            f = open(filepath, 'w')
            f.write(content.encode(DEFAULT_ENCODING))
            f.close()
        except Exception as e:
            print '[memcachelocal] Failed to save cache file (%s): %s' % \
                (filepath, unicode(e))
        else:
            print '[memcachelocal] Cache file saved (%s), size: %d.' % \
                (filepath, len(content))
