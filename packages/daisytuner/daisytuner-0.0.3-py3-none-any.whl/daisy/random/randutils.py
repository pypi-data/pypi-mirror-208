import itertools
import dace
import random

from collections import OrderedDict

ARRAY_MIN_TOTAL_SIZE = 4
ARRAY_MAX_TOTAL_SIZE = 128 * 128 * 128 * 128


DTYPES = [
    dace.bool,
    dace.int8,
    dace.int16,
    dace.int32,
    dace.float32,
    dace.float64,
]


def array_like(
    sdfg,
    array: str,
    transient: bool = False,
    permute_strides: bool = False,
):
    desc = sdfg.arrays[array]
    name, desc = sdfg.add_array(
        f"array_{len(sdfg.arrays)}",
        shape=desc.shape,
        strides=desc.strides,
        dtype=desc.dtype,
        transient=transient,
    )

    dims = len(desc.shape)
    if dims > 1 and permute_strides and random.uniform(0.0, 1.0) < 0.33:
        perm = list(range(dims))
        random.shuffle(perm)

        stride = 1
        strides = [1] * dims
        for i in range(dims):
            strides[perm[i]] = stride
            stride = stride * desc.shape[perm[i]]

        sdfg._arrays[name].strides = strides

    return name


def array(
    sdfg,
    dims: int = 1,
    shape=None,
    datatype=None,
    transient: bool = False,
    permute_strides: bool = True,
):
    if datatype is None:
        datatype = random.choice(DTYPES)

    if shape is None:
        min_size = int(ARRAY_MIN_TOTAL_SIZE ** (1 / dims))
        max_size = int(ARRAY_MAX_TOTAL_SIZE ** (1 / dims))

        shape = []
        for _ in range(dims):
            shape.append(random.randint(min_size, max_size))
        shape = tuple(shape)

    name, desc = sdfg.add_array(
        f"array_{len(sdfg.arrays)}", shape=shape, dtype=datatype, transient=transient
    )

    if dims > 1 and permute_strides and random.uniform(0.0, 1.0) < 0.33:
        perm = list(range(dims))
        random.shuffle(perm)

        stride = 1
        strides = [1] * dims
        for i in range(dims):
            strides[perm[i]] = stride
            stride = stride * shape[perm[i]]

        sdfg._arrays[name].strides = strides

    return name


def scalar(sdfg, datatype=None, transient: bool = True):
    if datatype is None:
        datatype = random.choice(DTYPES)

    scalar = f"scalar_{len(sdfg.arrays)}"
    sdfg.add_scalar(
        name=scalar, dtype=datatype, transient=transient, find_new_name=True
    )
    return scalar


def infer_dtype(dtypes):
    dtype = 0
    for dtype_ in dtypes:
        order = DTYPES.index(dtype_)
        if order == 0 and dtype > 0:
            raise ValueError("Unable to determine dtype")

        if order > dtype:
            dtype = order

    return DTYPES[dtype]


def infer_largest_common_dimensions(shapes):
    shape = shapes[0]
    for shape_ in shapes[1:]:
        if len(shape_) > len(shape):
            shape = shape_

    try:
        for shape_ in shapes:
            if shape_ == (1,):
                continue

            tmp = list(shape)
            for dim in shape_:
                i = tmp.index(dim)
                tmp.pop(i)
    except:
        raise ValueError("No common dimensions found")

    return shape


def infer_map_ranges(out_shape):
    ranges = OrderedDict()
    for i, dim in enumerate(out_shape):
        ranges[f"i_{i}"] = f"0:{dim}"

    return ranges


def matching_shape(shape, array_shapes):
    ps = powerset(shape)

    shapes = []
    for s in ps:
        perms = list(itertools.permutations(s))
        for perm in perms:
            if perm == (1,):
                continue

            if perm in array_shapes:
                shapes.append(perm)

    if not shapes:
        return None

    new_shape = random.choice(shapes)
    return new_shape


def powerset(iterable):
    xs = list(iterable)
    # note we return an iterator rather than a list
    return itertools.chain.from_iterable(
        itertools.combinations(xs, n) for n in range(len(xs) + 1)
    )
