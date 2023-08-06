import uuid
import dace
import random
import itertools

from collections import defaultdict
from typing import DefaultDict, List, Dict

from daisy.random import randexpr
from daisy.random import randutils


def convolve(
    sdfg: dace.SDFG,
    state: dace.SDFGState,
    access_nodes: Dict[str, dace.nodes.AccessNode],
    arrays: DefaultDict,
    rng,
    max_offset=3,
) -> List[dace.nodes.AccessNode]:
    # Draw main input
    while True:
        in_array = random.choice(list(access_nodes.keys()))
        if not isinstance(sdfg._arrays[in_array], dace.data.Scalar):
            break

    in_shape = sdfg._arrays[in_array].shape
    in_dtype = sdfg._arrays[in_array].dtype

    sources = [in_array]
    shapes = [in_shape]
    dtypes = [in_dtype]
    source_access_nodes = [access_nodes[in_array]]
    while rng.random() < 0.5:
        shape_ = randutils.matching_shape(in_shape, arrays.keys())
        if shape_ is None:
            break

        shape_ = tuple(shape_)
        if shape_ not in arrays:
            continue

        candidates = set(arrays[shape_])
        candidates = candidates.difference(set(sources))
        candidates = list(candidates)
        if not candidates:
            continue

        in_array_ = random.choice(candidates)
        in_shape_ = sdfg._arrays[in_array_].shape
        in_dtype_ = sdfg._arrays[in_array_].dtype
        if in_dtype == dace.bool or in_dtype_ == dace.bool and in_dtype != in_dtype_:
            continue

        sources.append(in_array_)
        shapes.append(in_shape_)
        dtypes.append(in_dtype_)

        if in_array_ not in access_nodes:
            access_nodes[in_array_] = state.add_read(in_array_)
        source_access_nodes.append(access_nodes[in_array_])

    # Assign inputs to output dimensions and determine filter sizes for each dimension
    max_out_shape = randutils.infer_largest_common_dimensions(shapes)
    filter_sizes = []
    bounds = defaultdict(list)
    for i in range(len(sources)):
        source = sources[i]
        shape = shapes[i]

        available_dims = list(enumerate(max_out_shape))
        offsets = []
        for dim in shape:
            found = None
            for i in range(len(available_dims)):
                j, dim_ = available_dims[i]
                if dim == dim_:
                    found = i
                    break

            j, _ = available_dims[found]
            available_dims.pop(found)

            left_offset = random.randint(0, min(max_offset, dim - 1))
            right_offset = random.randint(0, min(max_offset, dim - 1 - left_offset))
            offsets.append((j, left_offset, right_offset))

            bounds[j].append((left_offset, right_offset))

        filter_sizes.append(offsets)

    # Determine out shape and infer out array
    out_shape = []
    max_left_offsets = {}
    for i, dim in enumerate(max_out_shape):
        dim_bounds = bounds[i]
        max_left_offset = 0
        max_right_offset = 0
        for left_offset, right_offset in dim_bounds:
            if left_offset > max_left_offset:
                max_left_offset = left_offset
            if right_offset > max_right_offset:
                max_right_offset = right_offset

        effective_dim = dim - max_left_offset - max_right_offset
        out_shape.append(effective_dim)

        max_left_offsets[i] = max_left_offset

    out_dtype = randutils.infer_dtype(dtypes)
    out_array = randutils.array(
        sdfg,
        shape=out_shape,
        datatype=out_dtype,
        transient=True,
        permute_strides=(rng.random() < 0.25),
    )
    arrays[tuple(out_shape)].append(out_array)

    # Infer map range from out shape
    ranges = randutils.infer_map_ranges(out_shape)

    # Construct out memlet
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

    # Infer in memlets
    read_memlets = {}
    for i in range(len(sources)):
        source = sources[i]
        shape = shapes[i]
        offsets = filter_sizes[i]

        accesses = []
        for j, dim in enumerate(shape):
            k, left_offset, right_offset = offsets[j]
            max_left_offset = max_left_offsets[k]

            dim_accesses = []
            for o in range(0, left_offset + right_offset + 1):
                access = f"i_{j} + {o} + {max_left_offset - left_offset}"
                dim_accesses.append(access)

            accesses.append(dim_accesses)

        accesses = itertools.product(*accesses)
        accesses = list(map(lambda a: ",".join(a), list(accesses)))
        k = rng.integers(low=1, high=min(len(accesses), 127) + 1)
        accesses = random.choices(accesses, k=k)
        for access in accesses:
            read_memlets[f"__in{len(read_memlets) + 1}"] = dace.Memlet(
                data=source, subset=access
            )

    expr = randexpr.aggregate(read_memlets, dtype=out_dtype)
    code = f"""__out = {expr}"""
    tasklet, map_entry, map_exit = state.add_mapped_tasklet(
        name="stencil_" + str(uuid.uuid1()).replace("-", "_"),
        map_ranges=ranges,
        inputs=read_memlets,
        code=code,
        outputs=write_memlets,
    )

    for i in range(len(sources)):
        state.add_edge(
            source_access_nodes[i],
            None,
            map_entry,
            None,
            memlet=dace.Memlet.from_array(sources[i], sdfg.arrays[sources[i]]),
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
