from collections import defaultdict
import dace
import random

from typing import DefaultDict
from numpy.random import default_rng

import daisy.random.augmentations as augmentations
import daisy.random.randutils as randutils

from daisy.random.patterns import (
    convolve,
    element_wise,
    boolean_mask,
    transpose,
    reduce,
)
from dace.transformation.interstate import InlineSDFG


def randsdfg(
    name: str,
    max_stages: int = 48,
    max_dims: int = 10,
    rng=default_rng(42),
):
    """
    Returns a random SDFG.

    :param name: name of the SDFG.
    """
    sdfg = dace.SDFG(name)

    # Add initial set of input arrays
    arrays = defaultdict(list)
    for _ in range(10):
        dims = min(rng.poisson(lam=2.0) + 1, max_dims)
        array = randutils.array(
            sdfg,
            dims=dims,
            transient=False,
            permute_strides=True,
        )
        shape = sdfg._arrays[array].shape
        arrays[shape].append(array)

    # Add single state
    state = sdfg.add_state("state_0", is_start_state=True)
    arrays = _randstate(sdfg, state, max_stages=max_stages, arrays=arrays, rng=rng)

    # Remove unused input arrays
    used_arrays = set()
    for nsdfg in sdfg.all_sdfgs_recursive():
        for state in nsdfg.nodes():
            for dnode in state.nodes():
                if not isinstance(dnode, dace.nodes.AccessNode):
                    continue

                used_arrays.add(dnode.data)

    for shapes in arrays.values():
        for array in shapes:
            if array not in used_arrays:
                for nsdfg in sdfg.all_sdfgs_recursive():
                    if array in nsdfg.arrays:
                        del sdfg.arrays[array]

    # Fill missing values
    sdfg.fill_scope_connectors()

    # Expand non-fused reduce
    sdfg.expand_library_nodes()

    # Fuse MapReduce
    sdfg.apply_transformations_repeated(InlineSDFG)

    # Augment
    augmentations.otf_map_fusion(sdfg, rng=rng)
    augmentations.map_dim_shuffle(sdfg, rng=rng)
    # augmentations.map_tiling(sdfg, rng=rng)
    # augmentations.in_local_storage(sdfg, rng=rng)
    # augmentations.out_local_storage(sdfg, rng=rng)

    # Validate
    sdfg.validate()

    sdfg_js = sdfg.to_json()
    sdfg_ = sdfg.from_json(sdfg_js)

    return sdfg_


def _randstate(
    sdfg: dace.SDFG, state: dace.SDFGState, max_stages: int, arrays: DefaultDict, rng
):
    num_stages = rng.integers(low=1, high=max_stages + 1)
    array_list = [array for group in arrays.values() for array in group]

    access_nodes = {}
    for _ in range(num_stages):
        # Add new access node
        if not access_nodes or rng.random() < 0.10:
            new_access = None
            for _ in range(10):
                array = random.choice(array_list)
                if array not in access_nodes and not isinstance(
                    sdfg._arrays[array], dace.data.Scalar
                ):
                    new_access = array
                    break

            if new_access is not None:
                access_nodes[new_access] = state.add_read(new_access)

        # Add new pattern
        pattern_dice = rng.random()
        if pattern_dice < 0.1:
            dst_access_nodes = reduce(
                sdfg, state=state, access_nodes=access_nodes, arrays=arrays, rng=rng
            )
        elif pattern_dice < 0.4:
            dst_access_nodes = transpose(
                sdfg, state=state, access_nodes=access_nodes, arrays=arrays, rng=rng
            )
        elif pattern_dice < 0.6:
            dst_access_nodes = element_wise(
                sdfg, state=state, access_nodes=access_nodes, arrays=arrays, rng=rng
            )
        elif pattern_dice < 0.7:
            dst_access_nodes = boolean_mask(
                sdfg, state=state, access_nodes=access_nodes, arrays=arrays, rng=rng
            )
        else:
            dst_access_nodes = convolve(
                sdfg, state=state, access_nodes=access_nodes, arrays=arrays, rng=rng
            )

        for access_node in dst_access_nodes:
            access_nodes[access_node.data] = access_node

    # Cleanup nodes and set non-transient
    for node in access_nodes.values():
        if state.in_degree(node) == 0 and state.out_degree(node) == 0:
            state.remove_node(node)

            continue

        if state.out_degree(node) == 0:
            sdfg.arrays[node.data].transient = False

    return arrays
