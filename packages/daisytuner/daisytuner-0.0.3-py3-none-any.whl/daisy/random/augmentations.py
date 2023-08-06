import dace
import random

from dace.transformation.dataflow import (
    MapTiling,
    MapDimShuffle,
    OTFMapFusion,
    InLocalStorage,
    OutLocalStorage,
)
from dace.transformation.subgraph import helpers
from dace.transformation.optimizer import Optimizer


def map_dim_shuffle(sdfg, rng):
    for nsdfg in sdfg.all_sdfgs_recursive():
        for state in nsdfg.nodes():
            for node in state.nodes():
                if not isinstance(node, dace.nodes.MapEntry) or rng.random() < 0.5:
                    continue

                perm = list(node.map.params)
                random.shuffle(perm)
                MapDimShuffle.apply_to(
                    nsdfg,
                    map_entry=node,
                    options={"parameters": perm},
                    verify=True,
                    save=False,
                    annotate=False,
                )


def map_tiling(sdfg, rng):
    for nsdfg in sdfg.all_sdfgs_recursive():
        for state in nsdfg.nodes():
            top_level_maps = helpers.get_outermost_scope_maps(nsdfg, graph=state)
            for map_entry in top_level_maps:
                if rng.random() < 0.75:
                    continue

                dims = len(map_entry.map.params)
                tile_sizes = [2 ** rng.integers(low=1, high=10) for _ in range(dims)]
                MapTiling.apply_to(
                    nsdfg,
                    map_entry=map_entry,
                    options={"tile_sizes": tile_sizes},
                    verify=True,
                    save=False,
                    annotate=False,
                )


def in_local_storage(sdfg, rng):
    while rng.random() < 0.75:
        xforms = list(Optimizer(sdfg).get_pattern_matches(patterns=[InLocalStorage]))
        if len(xforms) == 0:
            break

        xform = random.choice(xforms)
        xform.apply(xform._sdfg.node(xform.state_id), xform._sdfg)


def out_local_storage(sdfg, rng):
    while rng.random() < 0.75:
        xforms = list(Optimizer(sdfg).get_pattern_matches(patterns=[OutLocalStorage]))
        if len(xforms) == 0:
            break

        xform = random.choice(xforms)
        xform.apply(xform._sdfg.node(xform.state_id), xform._sdfg)


def otf_map_fusion(sdfg, rng):
    while rng.random() < 0.90:
        xforms = list(Optimizer(sdfg).get_pattern_matches(patterns=[OTFMapFusion]))
        if len(xforms) == 0:
            # StopIteration
            break

        xform = random.choice(xforms)
        xform.apply(xform._sdfg.node(xform.state_id), xform._sdfg)
