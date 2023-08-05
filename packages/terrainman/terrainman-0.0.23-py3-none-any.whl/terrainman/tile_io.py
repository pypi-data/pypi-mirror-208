from http.cookiejar import CookieJar
import urllib.request
import base64
import zipfile
import io
import os
import rasterio
import numpy as np
import pickle
from typing import Union, Tuple
from abc import ABC
from netCDF4 import Dataset
import scipy

def _strip_tuple(t: tuple) -> tuple:
    """Returns a copy of a tuple-of-tuples with no extra layers such that `t[0][0]` is not a tuple

    :param t: Input tuple
    :type t: tuple
    :return: Same tuple, stripped of outer layers past the first
    :rtype: tuple
    """
    while isinstance(t[0], tuple):
        t = t[0]
    return (t,) # I am braindead and tired so this terribleness will have to do

class DataProduct(ABC):
    HTTP_ERR_MSG = "HTTP error occured, aborting..."
    DNE_MSG = "Data does not exist to download, skipping"
    EXISTS_MSG = "Data already downloaded, skipping"

    def _after_init(self):
        self._bad_input_path = os.path.join(self._storage_dir, 'bad_inputs.pkl')
        if not os.path.exists(self._bad_input_path):
            with open(os.path.join(self._bad_input_path), 'wb') as f:
                pickle.dump([], f)

    def _before_request(self, *args):
        try:
            os.environ['EARTHDATA_USERNAME']
            os.environ['EARTHDATA_PASSWORD']
        except KeyError as e:
            print("\nEnvironmental variables 'EARTHDATA_USERNAME' and 'EARTHDATA_PASSWORD' must be set!\nRegister at https://urs.earthdata.nasa.gov/users/new and set them with either:\n    - os.environ['EARTHDATA_USERNAME'] = '<your_username>'\n      os.environ['EARTHDATA_PASSWORD'] = '<your_password>'\n    - Create a .env.shared file in the calling directory containing\nEARTHDATA_USERNAME=<your_username>\nEARTHDATA_PASSWORD=<your_password>")
            raise
        efname = self._set_fnames(*args)
        if self._is_fname_bad(efname):
            print(self.DNE_MSG)
            return False
        print(f"Checking if {efname} is in {self._storage_dir}")
        if efname in os.listdir(self._storage_dir):
            print(self.EXISTS_MSG)
            return False
        print("File not found in storage, proceeding to download...")
        return True

    def _make_request(self, *args):
        print(f"Downloading {self.extracted_fname}...")
        self.request_url = f'{self.url_base}{self.url_fname}'
        print(f"Using: {self.request_url}")

        cj = CookieJar()
        credentials = ('%s:%s' % (os.environ['EARTHDATA_USERNAME'], os.environ['EARTHDATA_PASSWORD']))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        req = urllib.request.Request(self.request_url, None, {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Encoding': 'gzip, deflate, sdch','Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive', 'User-Agent': u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                                                'Authorization': 'Basic %s' % encoded_credentials.decode("ascii")})

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

        try:
            self.response = opener.open(req)
        except urllib.error.HTTPError as e:
            print(self.HTTP_ERR_MSG)
            self._store_bad_input(*args)
            self.response = None
    
    def _after_request(self):
        if self.response is not None:
            if self.download_format == "zip":
                z = zipfile.ZipFile(io.BytesIO(self.response.read()))
                z.extractall(self._storage_dir)
                print("Done.")
            else:
                bytesio_object = io.BytesIO(self.response.read())
                with open(os.path.join(self._storage_dir,self.extracted_fname), "wb") as f:
                    f.write(bytesio_object.getbuffer())
        else:
            return
    
    def _is_fname_bad(self, fname: str) -> bool:
        bad_fnames = self._load_bad_fnames()
        return fname in bad_fnames

    def _is_input_bad(self, *args) -> bool:
        efname = self._set_fnames(*args)
        return self._is_fname_bad(efname)
    
    def _load_bad_fnames(self) -> list[str]:
        with open(self._bad_input_path, 'rb') as f:
            return pickle.load(f)
    
    def _store_bad_fname(self, fname: str) -> None:
        x = self._load_bad_fnames()
        x.append(fname)
        with open(self._bad_input_path, 'wb') as f:
            pickle.dump(x, f)
    
    def _store_bad_input(self, *args) -> None:
        self._store_bad_fname(self._set_fnames(*args))
    
    def _load(self, *args) -> Union[np.ndarray, Dataset]:
        efname = self._set_fnames(*args)
        fpath = os.path.join(self._storage_dir, efname)
        if self.save_format == "hgt":
            with rasterio.open(fpath) as src:
                return src.read().squeeze()
        elif self.save_format == "nc":
            return Dataset(fpath, "r", format="NETCDF4")

    def _load_from_args(self, args: tuple[tuple], /, squeeze: bool = True):
        data = []
        for input_set in _strip_tuple(args):
            if self._is_input_bad(*input_set):
                print(f"Loading tile for {input_set} skipped, tile does not exist")
                data.append(None)
                continue
            data.append(self._load(*input_set))
        return data
    
    def _download_from_args(self, *args: Union[tuple[tuple], tuple]):
        for input_set in _strip_tuple(args):
            if self._before_request(*input_set):
                self._make_request(*input_set)
                self._after_request()


class TerrainDataHandler(DataProduct):
    def __init__(self) -> None:
        self._storage_dir = os.path.join(os.environ['TERRAIN_DATA'], 'terrain')
        self.url_base = 'https://e4ftl01.cr.usgs.gov/DP133/SRTM/SRTMGL1.003/2000.02.11/'
        self.download_format = "zip"
        self.save_format = "hgt"
        self.HTTP_ERR_MSG = "HTTP error occured, likely because tile is ocean, aborting..."
        self.DNE_MSG = "Tile does not exist, likely because it's ocean, skipping"
        self.EXISTS_MSG = "Tile already downloaded, skipping"

        self._after_init()
    
    def _set_fnames(self, lat: int, lon: int) -> str:
        tile_lon_str = f'{"W" if lon < 0 else "E"}{abs(lon):03}'
        tile_lat_str = f'{"N" if lat > 0 else "S"}{abs(lat):02}'
        extracted_fname =  f'{tile_lat_str}{tile_lon_str}.hgt'
        url_fname = f'{tile_lat_str}{tile_lon_str}.SRTMGL1.hgt.zip'
        self.extracted_fname = extracted_fname
        self.url_fname = url_fname
        return self.extracted_fname

    def download_tile(self, lat: int, lon: int) -> None:
        """Downloads [1 deg x 1 deg] a SRTM 30 meter resolution terrain tile for a given (integer) latitude and longitude pair, requires `os.environ['EARTHDATA_USERNAME']` and `os.environ['EARTHDATA_PASSWORD']` to be defined

        :param lat: Latitude [deg]
        :type lat: int
        :param lon: Longitude [deg]
        :type lon: int
        """
        self._download_from_args((lat, lon))
    
    def load_tile(self, lat: int, lon: int) -> np.ndarray:
        elev_grid = self._load_from_args((lat, lon))[0]
        if elev_grid is not None:
            lat_space = (lat+1) - np.linspace(0,1,elev_grid.shape[0])
            lon_space = lon + np.linspace(0,1,elev_grid.shape[0])
            return SrtmTile(lat_space, lon_space, elev_grid)
            return tile
        return None

    def load_tiles_containing(self, lat: np.ndarray, lon: np.ndarray) -> list[np.ndarray]:
        lat, lon = np.array([lat]).flatten(), np.array([lon]).flatten()
        self.download_tiles_containing(lat, lon)
        unique_lat_lons = self._unique_tile_lat_lon_pairs(lat, lon)
        return [self.load_tile(*args) for args in unique_lat_lons] if len(unique_lat_lons) > 1 \
            else self.load_tile(*unique_lat_lons[0])

    def download_tiles_containing(self, lat: np.ndarray, lon: np.ndarray) -> None:
        """Downloads [1 deg x 1 deg] SRTM 30 meter resolution terrain tiles to cover all latitude and longitudes input, requires `os.environ['EARTHDATA_USERNAME']` and `os.environ['EARTHDATA_PASSWORD']` to be defined

        :param lat: Latitude [deg]
        :type lat: np.ndarray
        :param lon: Longitude [deg]
        :type lon: np.ndarray
        """
        unique_lat_lons = self._unique_tile_lat_lon_pairs(lat, lon)
        print(f"Downloading tiles for {', '.join([self._set_fnames(*args) for args in unique_lat_lons])}")
        self._download_from_args(unique_lat_lons)

    def _unique_tile_lat_lon_pairs(self, lat: np.ndarray, lon: np.ndarray) -> list[Tuple[int, int]]:
        lat_lon_dec = np.vstack((lat.flatten(), lon.flatten())).T
        # lat_lon_int = np.hstack((np.floor(lat_lon_dec[:,[0]]), np.ceil(lat_lon_dec[:,[1]])))
        lat_lon_int = np.floor(lat_lon_dec)
        unique_lat_lons = np.unique(lat_lon_int, axis=0)
        unique_lat_lons = np.array(unique_lat_lons, np.int32)
        return tuple(map(tuple, unique_lat_lons))
    

class SrtmTile():
    """Represents a 1 x 1 degree terrain tile for Shuttle Radar Terrain Mission (SRTM) data
    """
    def __init__(self, lat_space: np.ndarray, lon_space: np.ndarray, elev_grid: np.ndarray) -> None:
        self.lat_space, self.lon_space = lat_space, lon_space
        self.lat_grid, self.lon_grid = np.meshgrid(lat_space, lon_space)
        self.elev_grid = elev_grid
    
    def interpolate(self, lat_deg: Union[float, np.ndarray], lon_deg: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Interpolates within the latitude/longitude 

        :param lat_deg: _description_
        :type lat_deg: float or np.ndarray
        :param lon_deg: _description_
        :type lon_deg: float or np.ndarray
        :raises NotImplemented: _description_
        :return: _description_
        :rtype: float or np.ndarray
        """
        kwargs = {'points': (self.lat_space, self.lon_space), 
                  'values': self.elev_grid,
                  'fill_value': np.nan,
                  'bounds_error': False}
        if isinstance(lat_deg, np.ndarray):
            return scipy.interpolate.interpn(**kwargs,
                                    xi=np.hstack((lat_deg.reshape(lat_deg.size,1), lon_deg.reshape(lat_deg.size,1)))).reshape(lat_deg.shape)
        elif isinstance(lat_deg, float):
            return scipy.interpolate.interpn(**kwargs,
                                    xi=np.hstack((lat_deg, lon_deg)))[0]
        else:
            raise NotImplemented("Inputs must be either floats or np.ndarrays")
