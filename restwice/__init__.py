try:
    # In App Engine
    from .urlfetch_client import UrlFetchClient
    RestClient = UrlFetchClient
except ImportError:
    # Otherwise we use Requests
    from .requests_client import RequestsClient
    RestClient = RequestsClient

from .memcache_local import MemcacheLocal
