import shutil
import pandas as pd

from abc import ABC, abstractmethod

from typing import Dict
from pathlib import Path

from daisy.map_nest import MapNest


class Analysis(ABC):
    """
    The base class for analyses.
    """

    def __init__(self, cache_path: Path, map_nest: MapNest) -> None:
        self._cache_path = cache_path
        self._map_nest = map_nest

    @abstractmethod
    def analyze(self) -> pd.DataFrame:
        pass

    def clear(self) -> Dict:
        shutil.rmtree(self._cache_path)
        self._cache_path.mkdir(exist_ok=False, parents=False)
