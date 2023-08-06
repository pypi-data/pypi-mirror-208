import pandas as pd

from typing import List

from abc import ABC, abstractmethod


class PerformanceMetrics(ABC):
    def __init__(self, arch: str, groups: List[str]) -> None:
        self._arch = arch
        self._groups = groups

    @abstractmethod
    def compute(self, counters: pd.DataFrame) -> pd.DataFrame:
        pass

    @classmethod
    def create(cls, arch: str, groups: List[str]):
        if arch == "broadwellEP":
            from daisy.analysis.performance_metrics.broadwellEP_performance_metrics import (
                BroadwellEPPerformanceMetrics,
            )

            return BroadwellEPPerformanceMetrics(groups=groups)
        elif arch == "haswellEP":
            from daisy.analysis.performance_metrics.haswellEP_performance_metrics import (
                HaswellEPPerformanceMetrics,
            )

            return HaswellEPPerformanceMetrics(groups=groups)
        elif arch == "skylake":
            from daisy.analysis.performance_metrics.skylakeX_performance_metrics import (
                SkylakePerformanceMetrics,
            )

            return SkylakePerformanceMetrics(groups=groups)
        elif arch == "skylakeX":
            from daisy.analysis.performance_metrics.skylakeX_performance_metrics import (
                SkylakeXPerformanceMetrics,
            )

            return SkylakeXPerformanceMetrics(groups=groups)
        elif arch == "zen":
            from daisy.analysis.performance_metrics.zen_performance_metrics import (
                ZenPerformanceMetrics,
            )

            return ZenPerformanceMetrics(groups=groups)
        elif arch == "zen2":
            from daisy.analysis.performance_metrics.zen2_performance_metrics import (
                Zen2PerformanceMetrics,
            )

            return Zen2PerformanceMetrics(groups=groups)
        elif arch == "zen3":
            from daisy.analysis.performance_metrics.zen3_performance_metrics import (
                Zen3PerformanceMetrics,
            )

            return Zen3PerformanceMetrics(groups=groups)
        else:
            raise NotImplementedError("Unsupported architecture")
