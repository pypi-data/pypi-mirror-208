import os
import copy
import math
import json
import dace
import numpy as np
import pandas as pd

from typing import Dict, List

from daisy.measure import measure, random_arguments

from daisy.map_nest import MapNest
from daisy.utils import host
from daisy.architecture import architecture, minimal_groups, _GPU_ARCHS
from daisy.analysis.analysis import Analysis
from daisy.analysis.performance_metrics.performance_metrics import PerformanceMetrics


SPECIAL_COUNTERS = set(
    [
        "CPU_CLK_UNHALTED_CORE",
        "CPU_CLK_UNHALTED_REF",
        "CPU_CLOCKS_UNHALTED",
        "CPU_CYCLES",
        "ACTUAL_CPU_CLOCK",
        "MAX_CPU_CLOCK",
    ]
)

MEASUREMENTS = 10


class Profiling(Analysis):
    """
    Performance metrics measured through LIKWID.
    """

    def __init__(
        self,
        map_nest: MapNest,
        hostname: str = None,
        arch: str = None,
        groups: List[str] = None,
        arguments: Dict = None,
    ) -> None:
        if hostname is not None and arch is None:
            raise ValueError("Specify architecture when using hostname")

        self._hostname = hostname
        self._arch = arch
        self._groups = groups
        if self._hostname is None:
            self._hostname = host()
            self._arch = architecture()["cpu"]

        if self._groups is None:
            self._groups = minimal_groups(self._arch)

        super().__init__(
            cache_path=map_nest.cache_folder
            / "analysis"
            / "instrumentation"
            / self._hostname,
            map_nest=map_nest,
        )

        self._arguments = arguments
        self._counters = None

    def analyze(self, cache_only: bool = False) -> pd.DataFrame:
        raw_data = self._get_raw_data(cache_only=cache_only)
        counters = None
        for group in self._groups:
            ex = [] if counters is None else counters.columns
            group_counters = Profiling._process(
                raw_data[group], arch=self._arch, exclude=ex
            )
            if group_counters is None:
                continue

            if counters is None:
                counters = group_counters
            else:
                counters = pd.merge(
                    left=counters, right=group_counters, on=["THREAD_ID", "REPETITION"]
                )

        self._counters = counters
        return counters

    def _get_raw_data(self, cache_only: bool) -> Dict:
        report = {}

        for group in self._groups:
            group_cache_path = self._cache_path / f"{group}.json"
            if group_cache_path.is_file():
                group_report = json.load(open(group_cache_path, "r"))
            elif not cache_only:
                if (
                    self._arch == architecture()["cpu"]
                    or self._arch in architecture()["gpu"]
                ):
                    group_report = self._measure_group(group)
                else:
                    raise ValueError(
                        f"Cannot measure group for {self._arch} on current machine"
                    )
            else:
                raise ValueError(f"Group {group} not in cache")

            report[group] = group_report[group]

        return report

    def _measure_group(self, group: str) -> Dict:
        if self._arguments is None:
            self._arguments = random_arguments(self._map_nest.cutout)

        arguments = copy.deepcopy(self._arguments)

        if self._arch in _GPU_ARCHS:
            for state in self._map_nest.cutout.states():
                state.instrument = dace.InstrumentationType.LIKWID_GPU
            os.environ["LIKWID_GEVENTS"] = group
        else:
            for state in self._map_nest.cutout.states():
                state.instrument = dace.InstrumentationType.LIKWID_CPU
            os.environ["LIKWID_EVENTS"] = group

        runtime, _, _ = measure(
            self._map_nest.cutout, arguments=arguments, measurements=MEASUREMENTS
        )
        if runtime == math.inf:
            raise ValueError(f"Failed to measure {group} group")

        group_report = self._map_nest.cutout.get_latest_report()
        group_report = {
            group: {
                "durations": {
                    str(k): dict(v) for k, v in group_report.durations.items()
                },
                "counters": {str(k): dict(v) for k, v in group_report.counters.items()},
            }
        }

        group_cache_path = self._cache_path / f"{group}.json"
        self._cache_path.mkdir(exist_ok=True, parents=True)
        with open(group_cache_path, "w") as handle:
            json.dump(group_report, handle)

        self._map_nest.cutout.start_state.instrument = (
            dace.InstrumentationType.No_Instrumentation
        )

        return group_report

    def performance_metrics(self) -> pd.DataFrame:
        return PerformanceMetrics.create(self._arch, self._groups).compute(
            self._counters
        )

    @staticmethod
    def _process(data: Dict, arch: str, exclude: List = None) -> pd.DataFrame:
        counters = data["counters"]["(0, 0, -1)"]["state_0_0_-1"]

        threads = None
        num_threads = None
        if arch in _GPU_ARCHS:
            # GPUs
            threads = ["0"]
            num_threads = 1
        else:
            # Hardware threads
            for counter in SPECIAL_COUNTERS:
                if counter in counters:
                    threads = list(counters[counter].keys())
                    num_threads = len(threads)
                    break

        all_values = []
        for counter in counters:
            if exclude is not None and counter in exclude:
                continue

            if "0" in counters[counter]:
                reps = len(counters[counter]["0"])
            else:
                reps = len(counters[counter][0])

            values = np.zeros((num_threads, reps))
            for i in range(values.shape[0]):
                for j in range(values.shape[1]):
                    values[i, j] = counters[counter][threads[i]][-j]

            if counter == "CAS_COUNT_RD" or counter == "CAS_COUNT_WR":
                # Postfix
                values = np.hstack([values[:, 1:], values[:, 0][:, None]])

                num_channels = 8
                if arch == "BroadwellEP":
                    num_channels = 8
                if arch == "haswellEP":
                    num_channels = 8
                elif arch == "skylakeX":
                    num_channels = 6
                values = values.reshape(num_threads, -1, num_channels)
                values = np.sum(values, axis=-1).squeeze()

                # Postfix
                values = np.flip(values, axis=-1)

            all_values.append(values)

        if not all_values:
            return None

        all_values = np.stack(all_values, axis=2)

        df = []
        for thread_id in range(all_values.shape[0]):
            for rep in range(all_values.shape[1]):
                row = np.concatenate(
                    [all_values[thread_id, rep, :], np.array([thread_id, rep])]
                )[None, :]
                df.append(row)

        df = np.vstack(df)

        columns = list(counters.keys())
        for c in exclude:
            if c in columns:
                columns.remove(c)
        columns += ["THREAD_ID", "REPETITION"]

        df = pd.DataFrame(df, columns=columns)

        if exclude is None or not "TIME" in exclude:
            runtimes = (
                np.array(
                    [
                        np.array(measurements)
                        for _, measurements in data["durations"]["(0, 0, -1)"][
                            "Timer"
                        ].items()
                    ]
                )
                / 1e3  # Convert to seconds
            )
            runtimes = runtimes.reshape(-1)
            df["TIME"] = runtimes

        return df
