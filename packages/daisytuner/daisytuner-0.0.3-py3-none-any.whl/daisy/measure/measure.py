import dace
import math
import time
import numpy as np

import traceback
import multiprocessing as mp

ctx = mp.get_context("spawn")

from typing import Dict, Tuple

from dace.codegen.compiled_sdfg import CompiledSDFG, ReloadableDLL
from dace import SDFG, config, InstrumentationType


def measure(
    sdfg: dace.SDFG,
    arguments: Dict,
    max_variance: float = 0.1,
    measurements: int = None,
    timeout: float = None,
) -> Tuple[float, float]:
    """
    A helper function to measure the median runtime of a SDFG over several measurements. The measurement is executed in a subprocess that can be killed after a specific timeout. This function will add default Timer instrumentation to the SDFG and return the full SDFG's runtime. The instrumentation report with the individual runtimes and the additional instrumentation is available afterwards as well.

    :param SDFG: the SDFG to be measured.
    :param arguments: the arguments provided to the SDFG.
    :param timeout: optional timeout to kill the measurement.
    :return: a tuple of median runtime, time of the whole measurement and the modified arguments (results). The second time is useful to determine a tight timeout for a transformed SDFG.
    """
    with config.set_temporary("instrumentation", "report_each_invocation", value=False):
        with config.set_temporary("compiler", "allow_view_arguments", value=True):
            sdfg.instrument = InstrumentationType.Timer
            csdfg = sdfg.compile()

            proc = MeasureProcess(
                target=_measure,
                args=(
                    sdfg.to_json(),
                    sdfg.build_folder,
                    csdfg._lib._library_filename,
                    arguments,
                    max_variance,
                    measurements,
                ),
            )

            start = time.time()
            proc.start()
            proc.join(timeout)
            process_time = time.time() - start

            # Handle failure
            if proc.exitcode != 0:
                if proc.is_alive():
                    proc.kill()

                return math.inf, process_time, None

            if proc.exception:
                if proc.is_alive():
                    proc.kill()
                error, traceback = proc.exception
                print(error)
                print(traceback)

                return math.inf, process_time, None

            # Handle success
            if proc.is_alive():
                proc.kill()

            report = sdfg.get_latest_report()
            durations = list(report.durations.values())[0]
            durations = list(durations.values())[0]
            durations = list(durations.values())[0]
            durations = np.array(durations)

            # Median with 95% CI
            durations = np.sort(durations)
            median = np.median(durations)

            n = len(durations)
            lower_ci = int(math.floor((n - 1.96 * math.sqrt(n)) / 2))
            lower_ci = max(0, min(n - 1, lower_ci))

            upper_ci = 1 + int(math.ceil((n + 1.96 * math.sqrt(n)) / 2))
            upper_ci = max(0, min(n - 1, upper_ci))

            return (
                median,
                process_time,
                (durations[lower_ci], median, durations[upper_ci]),
            )


def _measure(
    sdfg_json: Dict,
    build_folder: str,
    filename: str,
    arguments: Dict,
    max_variance: float,
    measurements: int,
):
    sdfg = SDFG.from_json(sdfg_json)
    sdfg.build_folder = build_folder
    lib = ReloadableDLL(filename, sdfg.name)
    csdfg = CompiledSDFG(sdfg, lib, arguments.keys())

    with config.set_temporary("instrumentation", "report_each_invocation", value=False):
        with config.set_temporary("compiler", "allow_view_arguments", value=True):
            rel_var = 1e4
            runs = []
            while (measurements is None and rel_var >= max_variance) or (
                measurements is not None and len(runs) < measurements
            ):
                s = time.time()

                csdfg(**arguments)

                t = time.time() - s
                runs.append(t)

                if len(runs) >= 3:
                    arr = np.array(runs)
                    rel_var = np.var(arr) / np.mean(arr)

            csdfg.finalize()


class MeasureProcess(ctx.Process):
    def __init__(self, *args, **kwargs):
        ctx.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = ctx.Pipe()
        self._exception = None

    def run(self):
        try:
            ctx.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception
