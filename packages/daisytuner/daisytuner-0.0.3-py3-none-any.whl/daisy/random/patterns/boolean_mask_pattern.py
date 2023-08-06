import dace
import uuid
import random

from typing import List, DefaultDict, Dict

from daisy.random import randutils

from daisy.random import randexpr


def boolean_mask(
    sdfg: dace.SDFG,
    state: dace.SDFGState,
    access_nodes: Dict[str, dace.nodes.AccessNode],
    arrays: DefaultDict,
    rng,
) -> List[dace.nodes.AccessNode]:
    while True:
        in_array = random.choice(list(access_nodes.keys()))
        if not isinstance(sdfg._arrays[in_array], dace.data.Scalar):
            break

    in_shape = sdfg._arrays[in_array].shape
    in_dtype = sdfg._arrays[in_array].dtype
    src_access_node = access_nodes[in_array]

    # Infer out array
    out_shape = in_shape
    out_dtype = dace.bool
    out_array = randutils.array(
        sdfg,
        shape=out_shape,
        datatype=out_dtype,
        transient=True,
        permute_strides=(rng.random() < 0.25),
    )
    arrays[tuple(out_shape)].append(out_array)

    # Infer map ranges
    ranges = randutils.infer_map_ranges(out_shape)

    # Infer write memlet
    write_subset = []
    for i, dim in enumerate(out_shape):
        if rng.random() < 0.75:
            access = f"i_{i}"
        else:
            # Flip dimension
            access = f"{dim} - i_{i} - 1"

        write_subset.append(access)
    write_memlets = {
        "__out": dace.Memlet(data=out_array, subset=",".join(write_subset))
    }

    # Construct in memlet
    read_subset = []
    for i, dim in enumerate(in_shape):
        if rng.random() < 0.75:
            access = f"i_{i}"
        else:
            # Flip dimension
            access = f"{dim} - i_{i} - 1"
        read_subset.append(access)
    read_memlets = {"__in": dace.Memlet(data=in_array, subset=",".join(read_subset))}

    # Infer tasklet
    if in_dtype == dace.bool:
        expr = randexpr.unary_logical("__in")
    else:
        expr = randexpr.unary_conditional("__in")

    code = f"""__out = ({expr})"""
    tasklet, map_entry, map_exit = state.add_mapped_tasklet(
        name="boolean_mask_" + str(uuid.uuid1()).replace("-", "_"),
        map_ranges=ranges,
        inputs=read_memlets,
        code=code,
        outputs=write_memlets,
    )

    state.add_edge(
        src_access_node,
        None,
        map_entry,
        None,
        memlet=dace.Memlet.from_array(in_array, sdfg.arrays[in_array]),
    )

    dest_access_node = state.add_access(out_array)
    state.add_edge(
        map_exit,
        None,
        dest_access_node,
        None,
        memlet=dace.Memlet.from_array(out_array, sdfg.arrays[out_array]),
    )

    map_entry.map.collapse = random.randint(1, len(map_entry.map.params))

    return [dest_access_node]
