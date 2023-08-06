import dace
import random

from typing import List, DefaultDict, Dict
from daisy.random import randutils


def reduce(
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
    out_dtype = in_dtype
    out_shape = []
    k = rng.integers(low=1, high=len(in_shape) + 1)
    axes = sorted(random.sample(range(len(in_shape)), k=k))
    for i, dim in enumerate(in_shape):
        if i in axes:
            continue
        out_shape.append(dim)

    if len(out_shape) == 0 or out_shape == (1,):
        dest = randutils.scalar(sdfg, datatype=out_dtype, transient=True)
        arrays[(1,)].append(dest)
    else:
        dest = randutils.array(
            sdfg,
            shape=out_shape,
            datatype=out_dtype,
            transient=True,
            permute_strides=True,
        )
        arrays[tuple(out_shape)].append(dest)

    if out_dtype == dace.bool:
        ops = (("and", True), ("or", False))
    else:
        ops = (("+", 0), ("-", 0), ("*", 1))

    op, identity = random.choice(ops)
    wcr = f"lambda a, b: a {op} b"
    reduce_node = state.add_reduce(wcr=wcr, axes=axes, identity=identity)

    state.add_edge(
        src_access_node,
        None,
        reduce_node,
        None,
        memlet=dace.Memlet.from_array(in_array, sdfg.arrays[in_array]),
    )

    dest_access_node = state.add_access(dest)
    state.add_edge(
        reduce_node,
        None,
        dest_access_node,
        None,
        memlet=dace.Memlet.from_array(dest, dest_access_node.desc(sdfg)),
    )

    return [dest_access_node]
