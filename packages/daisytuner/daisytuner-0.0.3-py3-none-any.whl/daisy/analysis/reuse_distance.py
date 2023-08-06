import dace
import copy
import math
import json
import pandas as pd

from typing import Tuple
from collections import OrderedDict

from daisy.map_nest import MapNest
from daisy.analysis.analysis import Analysis


class ReuseDistance(Analysis):
    """
    Approximate cache simulation based on stack and reuse distance.

    References:
        Beyls, K. and D'Hollander, E. H. Reuse distance as a metric for cache behavior. In Proceedings of the IASTED Conference on Parallel and Distributed Computing and Systems, pp. 617-662, 2001.
    """

    def __init__(
        self, map_nest: MapNest, cacheline_size: int = 1024 * 1024, cache_size: int = 64
    ) -> None:
        assert (
            map_nest.is_chain
        ), "ReuseDistance currently only supports chain-like MapNest objects"
        super().__init__(
            cache_path=map_nest.cache_folder / "analysis" / "cache_simulator",
            map_nest=map_nest,
        )

        self._sdfg = map_nest.cutout
        self._maps = map_nest.maps_tree
        self._innermost_map = map_nest.innermost_maps[0]

        self._stack = OrderedDict()
        self._cacheline_size = cacheline_size
        self._cache_size = cache_size
        self._max_cachelines = math.floor(cache_size / cacheline_size)

        self._ranges = []
        map_entry = None
        while map_entry in self._maps:
            map_entry = self._maps[map_entry][0]
            rngs = zip(map_entry.map.params, map_entry.range.ranges)
            self._ranges.extend(rngs)

        self._in_memlets = [
            edge.data for edge in self._sdfg.start_state.out_edges(self._innermost_map)
        ]
        self._out_memlets = [
            edge.data
            for edge in self._sdfg.start_state.in_edges(
                self._sdfg.start_state.exit_node(self._innermost_map)
            )
        ]

    def analyze(self, max_steps: int = 1024) -> pd.Series:
        report_path = (
            self._cache_path
            / f"report__{self._cache_size}_{self._cacheline_size}_{max_steps}.json"
        )
        if report_path.is_file():
            report = json.load(open(report_path, "r"))
            report = pd.Series(report)
            return report

        self._stack.clear()

        iter_ranges = []
        rngs = copy.deepcopy(self._ranges)
        state = {}
        for i in _ranges_iterator(self._sdfg, rngs, state, self._sdfg.constants):
            iter_ranges.append(i)

            if len(iter_ranges) >= max_steps:
                break

        misses = 0
        hits = 0
        bytes_read = 0
        bytes_write = 0
        max_iters = min(max_steps, len(iter_ranges))
        for indices in iter_ranges[:max_iters]:
            sm = {**self._sdfg.constants, **indices}

            for memlet in self._in_memlets:
                if memlet.data is None:
                    continue

                array = self._sdfg._arrays[memlet.data]
                access = []
                if isinstance(array, dace.data.Scalar):
                    access.append(0)
                else:
                    for start, stop, step in memlet.subset:
                        assert step == 1
                        start = int(dace.symbolic.evaluate(start, symbols=sm))
                        access.append(start)

                cacheline = _cacheline_at(
                    self._sdfg,
                    array,
                    access,
                    cacheline_size=self._cacheline_size,
                    symbol_map=sm,
                )
                cacheline = (memlet.data, cacheline)
                if cacheline in self._stack:
                    # Cache hit
                    hits += 1
                    self._stack.move_to_end(cacheline, last=False)
                else:
                    misses += 1
                    bytes_read += self._cacheline_size
                    self._stack[cacheline] = True
                    self._stack.move_to_end(cacheline, last=False)

                if len(self._stack) > self._max_cachelines:
                    self._stack.popitem(last=True)

            for memlet in self._out_memlets:
                array = self._sdfg._arrays[memlet.data]
                access = []
                if isinstance(array, dace.data.Scalar):
                    access.append(0)
                else:
                    for start, stop, step in memlet.subset:
                        assert step == 1
                        start = int(dace.symbolic.evaluate(start, symbols=sm))
                        access.append(start)

                cacheline = _cacheline_at(
                    self._sdfg,
                    array,
                    access,
                    cacheline_size=self._cacheline_size,
                    symbol_map=sm,
                )
                cacheline = (memlet.data, cacheline)
                if cacheline in self._stack:
                    # Cache hit
                    hits += 1
                    self._stack.move_to_end(cacheline, last=False)
                else:
                    misses += 1
                    bytes_write += self._cacheline_size
                    self._stack[cacheline] = True
                    self._stack.move_to_end(cacheline, last=False)

                if len(self._stack) > self._max_cachelines:
                    self._stack.popitem(last=True)

        if misses == 0:
            miss_ratio = 0.0
        else:
            miss_ratio = misses / (hits + misses)

        report = {
            "iterations": max_iters,
            "hits": hits,
            "misses": misses,
            "miss_ratio": miss_ratio,
            "bytes_read": bytes_read,
            "bytes_write": bytes_write,
        }
        self._cache_path.mkdir(exist_ok=True, parents=True)
        with open(report_path, "w") as handle:
            json.dump(report, handle)

        report = pd.Series(report)
        return report


def _ranges_iterator(sdfg, ranges, state, symbol_map):
    if len(ranges) == 0:
        yield state
        return

    ranges_ = copy.deepcopy(ranges)
    var, (start, stop, step) = ranges_.pop(0)

    locals = {**symbol_map, **state}
    start = int(dace.symbolic.evaluate(start, symbols=locals))
    stop = int(dace.symbolic.evaluate(stop, symbols=locals))
    step = int(dace.symbolic.evaluate(step, symbols=locals))

    rng = range(start, stop + 1, step)

    state_ = copy.deepcopy(state)
    for index in rng:
        state_[var] = index
        yield from _ranges_iterator(
            sdfg, ranges_, state=copy.deepcopy(state_), symbol_map=symbol_map
        )


def _cacheline_at(
    sdfg, array: dace.data.Data, access: Tuple[int], cacheline_size: int, symbol_map
):
    assert len(access) == len(array.shape)
    element_size = array.dtype.bytes

    # Computing position in memory
    flat_index = array.start_offset
    for i in range(len(access)):
        flat_index += access[i] * int(
            dace.symbolic.evaluate(array.strides[i], symbols=symbol_map)
        )

    if isinstance(array, dace.data.Scalar):
        bytes_position = flat_index * element_size
        cacheline_index = math.floor(bytes_position / cacheline_size)
    else:
        bytes_position = flat_index * (element_size + array.alignment)
        cacheline_index = math.floor(bytes_position / cacheline_size)

    return cacheline_index
