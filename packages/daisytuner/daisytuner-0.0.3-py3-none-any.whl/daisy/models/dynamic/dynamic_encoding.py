import torch
import numpy as np

from abc import ABC, abstractmethod

from daisy.map_nest import MapNest
from daisy.architecture import minimal_groups
from daisy.analysis.profiling import Profiling


class DynamicEncoding(ABC):
    def __init__(self, map_nest: MapNest, hostname: str, arch: str) -> None:
        self._map_nest = map_nest
        self._hostname = hostname
        self._arch = arch
        self._encoding = None

    def encode(self, cache_only: bool = True) -> torch.tensor:
        if self._encoding is not None:
            return self._encoding

        # Gather instrumentation data
        instrumentation = Profiling(
            map_nest=self._map_nest,
            hostname=self._hostname,
            arch=self._arch,
            groups=minimal_groups(self._arch),
        )
        data = instrumentation.analyze(cache_only=cache_only)

        # Compute statistics over threads; median over repetitions
        data = data.groupby("REPETITION").agg(["min", "max", "sum", "mean", "std"])
        data = data.median()
        data = self._vectorize(data)

        self._encoding = torch.tensor(data, dtype=torch.float)[None, :]
        return self._encoding

    @abstractmethod
    def _vectorize(self, data) -> np.ndarray:
        pass

    @classmethod
    def _normalize(cls, counters, name) -> np.ndarray:
        stats = np.zeros(5)
        for i, stat in enumerate(["min", "max", "sum", "mean", "std"]):
            stats[i] = counters[name][stat]

        return stats

    @classmethod
    def create(cls, map_nest: MapNest, hostname: str, arch: str):
        if arch == "broadwellEP":
            from daisy.models.dynamic.broadwellEP_encoding import BroadwellEPEncoding

            return BroadwellEPEncoding(map_nest=map_nest, hostname=hostname)
        elif arch == "haswellEP":
            from daisy.models.dynamic.haswellEP_encoding import HaswellEPEncoding

            return HaswellEPEncoding(map_nest=map_nest, hostname=hostname)
        elif arch == "skylakeX":
            from daisy.models.dynamic.skylakeX_encoding import SkylakeXEncoding

            return SkylakeXEncoding(map_nest=map_nest, hostname=hostname)
        elif arch == "zen":
            from daisy.models.dynamic.zen_encoding import ZenEncoding

            return ZenEncoding(map_nest=map_nest, hostname=hostname)
        elif arch == "zen2":
            from daisy.models.dynamic.zen2_encoding import Zen2Encoding

            return Zen2Encoding(map_nest=map_nest, hostname=hostname)
        elif arch == "zen3":
            from daisy.models.dynamic.zen3_encoding import Zen3Encoding

            return Zen3Encoding(map_nest=map_nest, hostname=hostname)
        else:
            raise ValueError("Unsupported architecture: ", arch)
