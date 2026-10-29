'''
Download satellite images from the Mapbox Static Images API.
https://docs.mapbox.com/api/maps/static-images/
'''

import os
import requests

# Base URL. Logo and attribution are switched off as they would be burnt into
# the training images.
MAPBOX_ENDPOINT = (
    'https://api.mapbox.com/styles/v1/{style}/static/{lon},{lat},{zoom}'
    '/{width}x{height}?access_token={access_token}&attribution=false&logo=false'
    '&format={format}')

# Params
MAPBOX_STYLE = 'mapbox/satellite-v9'
MAPBOX_FORMAT = 'png'
MAX_SIZE = 1280


class MapboxStatic(object):

    def __init__(self, namespace=None, root_folder=None, style=MAPBOX_STYLE):
        self._namespace = namespace or 'mapbox'
        self._root_folder = root_folder or '/tmp'
        self._style = style
        if not os.path.isdir(self._root_folder):
            os.makedirs(self._root_folder)
            print('[mapbox static] Root folder created: %s' % self._root_folder)

    def get_filepath(self, element_id):
        filename = '%s_%s.%s' % (self._namespace, element_id, MAPBOX_FORMAT)
        return os.path.join(self._root_folder, filename)

    def get_url(self, latitude, longitude, mapbox_zoom, access_token,
                width=1280, height=1280):
        if width > MAX_SIZE or height > MAX_SIZE:
            raise ValueError('Mapbox static images are at most %dx%d pixels'
                             % (MAX_SIZE, MAX_SIZE))
        # mapbox_zoom uses 256-pixel tiles like the rest of cv4ag. Style-based
        # static images use 512-pixel tiles, i.e. the same scale is one zoom
        # level lower.
        return MAPBOX_ENDPOINT.format(
            style=self._style,
            lon=longitude,
            lat=latitude,
            zoom=mapbox_zoom - 1,
            width=width,
            height=height,
            format=MAPBOX_FORMAT,
            access_token=access_token)

    def download_tile(self, element_id, url, verbose=True):
        '''returns True if the tile is available (downloaded now or before)'''
        filepath = self.get_filepath(element_id=element_id)
        if os.path.isfile(filepath):
            if verbose:
                print('[mapbox static] Tile already downloaded (%s).' % filepath)
            return True
        if verbose:
            print('[mapbox static] Downloading tile (%s).' % filepath)
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            print('[mapbox static] Download failed (HTTP %d): %s'
                  % (response.status_code, response.text[:200]))
            return False

        # Detect if we have actual imagery here
        if len(response.content) < 500:
            if verbose:
                print('Ignoring downloaded file, it looks like an empty image. Check zoom level')
            return False
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return True
