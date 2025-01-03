import os
import tempfile
from dataclasses import dataclass
from functools import cache

import numpy as np
from utils import WWW, Log

from alt_lk.core.BBox import BBox
from alt_lk.core.LatLng import LatLng
from alt_lk.core.Resolution import Resolution
from alt_lk.data.AltFile import AltFile
from utils_future import SparseArrayFile

log = Log("Alt")


@dataclass
class Alt:
    alt_m: float

    def __str__(self):
        return f"{self.alt_m:,.0f}m / {self.alt_ft:,.0f}ft"

    FEET_PER_METER = 3.28084

    @property
    def alt_ft(self) -> float:
        return self.alt_m * Alt.FEET_PER_METER

    MIN_LATLNG = LatLng(5, 78)
    MAX_LATLNG = LatLng(9, 82)
    BBOX = BBox(MIN_LATLNG, MAX_LATLNG)
    MIN_LAT = MIN_LATLNG.lat
    MAX_LAT = MAX_LATLNG.lat
    LAT_SPAN = MAX_LAT - MIN_LAT
    MIN_LNG = MIN_LATLNG.lng

    RESOLUTION = Resolution(1, 3)

    COMBINED_FILE_NAME = f"alt.combined.lk.{RESOLUTION.file_code}.npz"
    COMBINED_DATA_FILE_PATH = os.path.join("data", COMBINED_FILE_NAME)
    COMBINED_DATA_FILE = SparseArrayFile(COMBINED_DATA_FILE_PATH)

    LOCAL_COMBINED_DATA_FILE_PATH = os.path.join(
        tempfile.gettempdir(), COMBINED_FILE_NAME
    )
    LOCAL_COMBINED_DATA_FILE = SparseArrayFile(LOCAL_COMBINED_DATA_FILE_PATH)

    URL_COMBILED_DATA = (
        "https://raw.githubusercontent.com"
        + "/nuuuwan/alt_lk"
        + f"/main/data/{COMBINED_FILE_NAME}"
    )

    @staticmethod
    @cache
    def matrix():
        log.debug("Loading matrix...")
        if Alt.LOCAL_COMBINED_DATA_FILE.exists:
            log.debug(f"Loading {Alt.LOCAL_COMBINED_DATA_FILE_PATH}...")
            return Alt.LOCAL_COMBINED_DATA_FILE.read()

        if Alt.COMBINED_DATA_FILE.exists:
            log.debug(f"Loading {Alt.COMBINED_DATA_FILE_PATH}...")
            data = Alt.COMBINED_DATA_FILE.read()
            Alt.LOCAL_COMBINED_DATA_FILE.write(data)
            return data

        log.info(f"Downloading from {Alt.URL_COMBILED_DATA} ...")
        WWW.download_binary(
            Alt.URL_COMBILED_DATA, Alt.LOCAL_COMBINED_DATA_FILE_PATH
        )
        data = Alt.LOCAL_COMBINED_DATA_FILE.read()
        return data

    @staticmethod
    def build_matrix():
        data = AltFile.get_combined_data(Alt.BBOX, Alt.RESOLUTION)
        Alt.COMBINED_DATA_FILE.write(data)
        return data

    @staticmethod
    @cache
    def latlng_to_indices(latlng: LatLng):
        dim1 = Alt.RESOLUTION.dim1
        lat, lng = latlng.tuple
        i_lat = (Alt.LAT_SPAN + 1) * dim1 - int((lat - Alt.MIN_LAT) * dim1)
        i_lng = int((lng - Alt.MIN_LNG) * dim1)

        return (i_lat, i_lng)

    @staticmethod
    @cache
    def indices_to_latlng(i_lat: int, i_lng: int) -> LatLng:
        dim1 = Alt.RESOLUTION.dim1
        lat = Alt.MIN_LAT + (Alt.LAT_SPAN + 1 - i_lat / dim1)
        lng = Alt.MIN_LNG + i_lng / dim1
        return LatLng(lat, lng)

    @staticmethod
    @cache
    def get_matrix_subset(bbox: BBox) -> np.array:
        data = Alt.matrix()
        min_latlng, max_latlng = bbox.tuple
        i_min_lat, i_min_lng = Alt.latlng_to_indices(min_latlng)
        i_max_lat, i_max_lng = Alt.latlng_to_indices(max_latlng)
        arr = np.array(data)
        arr_subset = arr[i_max_lat:i_min_lat, i_min_lng:i_max_lng]
        return arr_subset

    @staticmethod
    @cache
    def from_latlng(latlng: LatLng) -> "Alt":
        data = Alt.matrix()
        (i_lat, i_lng) = Alt.latlng_to_indices(latlng)
        return Alt(data[i_lat][i_lng])

    @staticmethod
    def list_from_latlng_list(latlng_list: list[LatLng]) -> list["Alt"]:
        return [Alt.from_latlng(latlng) for latlng in latlng_list]
