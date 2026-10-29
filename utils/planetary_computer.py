'''
Search and read open data from Microsoft Planetary Computer
(https://planetarycomputer.microsoft.com). No account is needed: data URLs
are signed with anonymous tokens.
'''
import time
from datetime import datetime, timezone

import requests

STAC_API = 'https://planetarycomputer.microsoft.com/api/stac/v1'
SAS_API = 'https://planetarycomputer.microsoft.com/api/sas/v1/token/'
# read cloud-optimized GeoTIFFs over HTTP without listing directories
GDAL_ENV = {'GDAL_DISABLE_READDIR_ON_OPEN': 'EMPTY_DIR',
            'GDAL_HTTP_MAX_RETRY': '5', 'GDAL_HTTP_RETRY_DELAY': '2'}

_tokens = {}


def year_range(year):
    return '%d-01-01T00:00:00Z/%d-12-31T23:59:59Z' % (int(year), int(year))


def search(collection, bbox, datetime=None):
    '''all STAC items of collection intersecting bbox (west,south,east,north in degrees)'''
    body = {'collections': [collection], 'bbox': list(bbox), 'limit': 1000}
    if datetime:
        body['datetime'] = datetime
    url = STAC_API + '/search'
    items = []
    while url:
        response = requests.post(url, json=body, timeout=120)
        response.raise_for_status()
        result = response.json()
        items += result['features']
        url = None
        for link in result.get('links', []):
            if link.get('rel') == 'next':
                url = link['href']
                body = link.get('body', body)
    return items


def sign(href, collection):
    '''href with a (cached) read token for collection'''
    token = _tokens.get(collection)
    if token is None or token[1] - time.time() < 300:
        response = requests.get(SAS_API + collection, timeout=60)
        response.raise_for_status()
        result = response.json()
        expiry = datetime.fromisoformat(result['msft:expiry'].replace('Z', '+00:00'))
        token = (result['token'], expiry.replace(tzinfo=expiry.tzinfo or timezone.utc).timestamp())
        _tokens[collection] = token
    return href + '?' + token[0]
