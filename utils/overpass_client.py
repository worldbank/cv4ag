'''
Query the Overpass API (OpenStreetMap) in chunks, with a local file cache
'''
import hashlib
import json
import os
import time

import numpy as np
import requests

OVERPASS_ENDPOINTS = {
    'de': 'https://overpass-api.de/api/interpreter',
    'kumi': 'https://overpass.kumi.systems/api/interpreter'}

OVERPASS_CACHE_FOLDER = '_cache_overpass'
OVERPASS_REQUESTS_TIMEOUT = 60 * 5  # 5 minutes
USER_AGENT = 'cv4ag (https://github.com/worldbank/cv4ag)'


class OverpassClient(object):
    def __init__(self, endpoint='de', cache_folder=OVERPASS_CACHE_FOLDER):
        self._endpoint = OVERPASS_ENDPOINTS.get(endpoint, endpoint)
        self._cache_folder = cache_folder

    def do_query(self, ql_text, retries=5):
        '''run a query (results are cached, safe to run multiple times)'''
        data = '[out:json][timeout:%d];' % (OVERPASS_REQUESTS_TIMEOUT - 30) + ql_text
        cache_file = None
        if self._cache_folder:
            os.makedirs(self._cache_folder, exist_ok=True)
            key = hashlib.sha1((self._endpoint + data).encode()).hexdigest()
            cache_file = os.path.join(self._cache_folder, key + '.json')
            if os.path.isfile(cache_file):
                with open(cache_file) as f:
                    return json.load(f)
        for attempt in range(retries):
            try:
                response = requests.post(self._endpoint, data={'data': data},
                                         headers={'User-Agent': USER_AGENT},
                                         timeout=OVERPASS_REQUESTS_TIMEOUT)
                if response.status_code == 200:
                    result = response.json()
                    if 'remark' in result and 'error' in result['remark'].lower():
                        raise ValueError(result['remark'])
                    break
                message = 'HTTP %d' % response.status_code
            except (requests.RequestException, ValueError) as e:
                message = str(e)
            wait = 5 * 2 ** attempt
            print('No answer received (%s). Try again in %ds...' % (message[:200], wait))
            time.sleep(wait)
        else:
            raise RuntimeError('Overpass query failed %d times' % retries)
        if cache_file:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        return result

    def get_bbox_elements(self, ql_template, bb_s, bb_w, bb_n, bb_e, samples=2):
        # Samples subdivides the bbox into smaller bboxes to make sure the
        # request doesn't timeout. For linspace below to work, we need this
        # number to be 2 or greater.
        assert samples >= 2

        # Track iterations
        total_iterations = (samples - 1) ** 2
        current_iteration = 0

        # Build ranges
        lat_range = np.linspace(bb_s, bb_n, num=samples)
        lon_range = np.linspace(bb_w, bb_e, num=samples)

        # Elements crossing chunk borders are returned more than once
        elements = {}
        for lat_index in range(samples - 1):
            for lon_index in range(samples - 1):
                current_iteration += 1
                print('Iteration %d/%d...' % (current_iteration, total_iterations))

                # Get the values and build query
                ql_text = ql_template.format(
                    query_bb_s=lat_range[lat_index], query_bb_w=lon_range[lon_index],
                    query_bb_n=lat_range[lat_index + 1], query_bb_e=lon_range[lon_index + 1])
                partial_elements = self.do_query(ql_text=ql_text).get('elements', [])
                print('Partials elements found: %d' % len(partial_elements))
                for element in partial_elements:
                    elements[(element['type'], element['id'])] = element

        # Done
        return list(elements.values())
