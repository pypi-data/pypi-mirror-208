import logging
from contextlib import suppress

import h5py
import numpy as np
import pandas as pd

from swdl.tools import PathLike

logger = logging.getLogger(__name__)


class MatchData:
    def __init__(self, match_id: str = ""):
        """An interface to store match data information.

        Provides basic operations on MatchData instances

        Args:
            match_id: The id if the match the data belongs to.
        """
        self.objects: pd.DataFrame = pd.DataFrame()
        self.events: pd.DataFrame = pd.DataFrame()
        self.camera_positions = pd.DataFrame()
        self.match_id = match_id

    def insert_objects(self, df: pd.DataFrame):
        self.objects = pd.concat([self.objects, df], ignore_index=True)

    @staticmethod
    def _save_split(df: pd.DataFrame, path: str, key: str):
        copy = df.copy()
        for column, dtype in df.dtypes.items():
            # Drop match_id as it is redundant with every object
            if column == "match_id":
                copy.drop(column, inplace=True, axis=1)
                continue
            if dtype != object:
                continue
            data = df[column].values.tolist()
            if not data:
                continue
            if isinstance(data[0], str):
                copy[column] = copy[column].astype(str)
                continue
            if not isinstance(data[0], np.ndarray):
                logger.warning("Storing custom objects may be inefficient")
                continue
            shape = data[0].shape
            if len(shape) > 1:
                logger.warning("Storing arrays with rank > 1 may be inefficient")
                continue
            dims = shape[0]
            if dims == 0:
                logger.warning(f"Dropping empty array {column}")
                copy.drop(column, inplace=True, axis=1)
                continue
            names = [str(column) + "#" + str(i) for i in range(dims)]
            copy[names] = data
            copy.drop(column, inplace=True, axis=1)
        copy.to_hdf(path, key=key, format="table")

    def save(self, path: PathLike):
        """Save MatchData to hdf5 format.

        The keys 'objects', 'events' and 'camera_positions' will be replaced if writing
            to an exsisting hdf5 file.
        Args:
            path: Path to store the file to.

        """
        self._save_split(self.objects, path, "objects")
        self._save_split(self.events, path, "events")
        self._save_split(self.camera_positions, path, "camera_positions")
        file = h5py.File(path, "a")
        if "meta" not in file.keys():
            ds = file.create_dataset("meta", dtype=int)
        else:
            ds = file["meta"]
        ds.attrs["match_id"] = self.match_id

    @staticmethod
    def _merge_arrays(df=pd.DataFrame):
        split_columns = [c for c in df.columns if "#" in c]
        new_columns = set(c.split("#")[0] for c in split_columns)
        for col in new_columns:
            old_cols = sorted(c for c in split_columns if c.startswith(col))
            df[col] = df[old_cols].values.tolist()
            df.drop(old_cols, inplace=True, axis=1)

    def load(self, path: PathLike, merge=True):
        """Load MatchData from hdf5 file.

        Overwrites the local members inplace.

        Args:
            path: Path to file to load from
            merge: Merge split arrays back to a single column
        """
        with pd.HDFStore(path, mode="r") as hdf_store:
            with suppress(KeyError):
                self.objects = hdf_store.get("objects")
                if merge:
                    self._merge_arrays(self.objects)
            with suppress(KeyError):
                self.events = hdf_store.get("events")
                if merge:
                    self._merge_arrays(self.events)
            with suppress(KeyError):
                self.camera_positions = hdf_store.get("camera_positions")
                if merge:
                    self._merge_arrays(self.camera_positions)
        file = h5py.File(path, "r")
        ds = file["meta"]
        self.match_id = ds.attrs["match_id"]
        if self.match_id:
            self.objects["match_id"] = self.match_id

    @staticmethod
    def load_timestamps(path: PathLike) -> pd.DataFrame:
        """Loads only the objects timestamps from a MatchData file"""
        with pd.HDFStore(path, mode="r") as hdf_store:
            ts = hdf_store.select(key="objects", columns=["timestamp_ns"])
        return ts

    @classmethod
    def from_file(cls, path: PathLike, merge=True):
        """Create MatchData from hdf5 file.

        Args:
        path: Path to file to load from
        merge: Merge split arrays back to a single column
        """

        match_data = cls()
        match_data.load(path, merge)

        return match_data
