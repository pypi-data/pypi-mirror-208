import re
import dace
import copy
import sympy as sp

from typing import Optional, Tuple

from dace.sdfg.nodes import *
from dace.sdfg.graph import MultiConnectorEdge
from dace.sdfg.nodes import *
from dace.subsets import Range, Indices
from dace import subsets

# default numerical parameters for the schedue generation
decompostition_params = [
    ("p", 8),
    ("Ss", 32 * 1024),
    ("S0", 512),
    ("S1", 512),
    ("S2", 512),
    ("S3", 512),
]


import dace.frontend.python.parser
import sys
import os


# ----------------------------------------
# various helper functions
# ----------------------------------------
def rng_global2dict(ranges_scopes):
    rng_dict = {}
    for scope, ranges in ranges_scopes.items():
        rng_dict = {**rng_dict, **rng_list2dict(ranges)}
    return rng_dict


def rng_list2dict(ranges) -> Dict[str, Tuple]:
    return dict([(it, (rng_low, rng_high)) for (it, rng_low, rng_high) in ranges])


def rng_dict2list(ranges_dict):
    return list(ranges_dict.items())


def strip(array_name_with_version: str) -> str:
    return "_".join(array_name_with_version.split("_")[:-1])


def get_access_from_memlet(
    memlet: dace.Memlet, iter_vars
) -> Tuple[str, str, Tuple[int]]:
    arrayName = memlet.data  # + "_" + str(memlet.soap_array.version)
    baseAccess = ""
    offsets = []
    for looop in memlet.subset.ndrange():
        if looop[0] != looop[1] or looop[2] != 1:
            raise ValueError("Malformed program")
        # check if we are updating only a subset of array. If yes, then this statement
        # does NOT count the array as a whole
        if not looop[0].free_symbols:
            # TODO: new experimental. Instead of discarding, we need to handle it
            if len(memlet.subset.ndrange()) > 1:
                # return (None, None, None)
                continue
            # this is the case when we have a WCR on a transient scalar
            else:
                continue

        # a) remove constants from the access function (e.g., A[i + N] -> A[i])
        # b) split dimensions with multiple iteration variables into multiple dimensions (e.g., A[i-k] -> A[i,k])
        [access, offset] = extract_access(looop[0], iter_vars)
        if access:
            baseAccess += str(access) + "*"
            offsets += offset
            # subtract the currently accessed iteration variable to avoid situations like e.g.,:
            # A[i,i] -> base_access = 'i*i'. It should be base_access = 'i' (just one i).
            iter_vars = iter_vars - access.free_symbols
    baseAccess = baseAccess[:-1]

    return (arrayName, baseAccess, tuple(offsets))


def base_in_list(base_str: str, swaplist: Dict[str, str]) -> bool:
    return any(
        any((re.search(r"\b%s\b" % iter, swap_el)) for swap_el in swaplist.keys())
        for iter in base_str.split("*")
    )


def swap_in_string(base_str, swaplist, inv_swaplist) -> str:
    if not base_in_list(base_str, swaplist) and not base_in_list(
        base_str, inv_swaplist
    ):
        return base_str
    if base_in_list(base_str, swaplist) and base_in_list(base_str, inv_swaplist):
        for iter_new, iter_old in swaplist.items():
            base_str = re.sub(iter_new, "tmppp", base_str)
            base_str = re.sub(iter_old, iter_new, base_str)
            base_str = re.sub("tmppp", iter_old, base_str)
        return base_str
    else:
        if base_in_list(base_str, swaplist):
            cur_swaplist = swaplist
        else:
            cur_swaplist = inv_swaplist
        rep = dict((re.escape(k), v) for k, v in cur_swaplist.items())
        pattern = re.compile(r"\b" + (r"\b|\b".join(rep.keys())) + r"\b")
        return pattern.sub(lambda m: rep[re.escape(m.group(0))], base_str)


def int_to_real(expr):
    """Remove floors and ceilings from the expression"""
    nexpr = expr
    if not isinstance(expr, sp.Basic):
        return expr

    a = sp.Wild("a")
    processed = 1
    while processed > 0:
        processed = 0
        for ceil in nexpr.find(sp.ceiling):
            # Simple ceiling
            m = ceil.match(sp.ceiling(a))
            if m is not None:
                nexpr = nexpr.subs(ceil, m[a])
                processed += 1
                continue

    processed = 1
    while processed > 0:
        processed = 0
        for fl in nexpr.find(sp.floor):
            # Simple ceiling
            m = fl.match(sp.floor(a))
            if m is not None:
                nexpr = nexpr.subs(fl, m[a])
                processed += 1
                continue

    return nexpr


def compare_Q(Q_1, Q_2):
    Ss = sp.sympify("Ss")
    Q_new_val = Q_1.subs(Ss, 10000)
    subsList = []
    for symbol in Q_new_val.free_symbols:
        subsList.append([symbol, 100000])
    Q_new_val = Q_new_val.subs(subsList)

    if Q_2 != 0:
        Q_old_val = Q_2.subs(Ss, 10000)
        subsList = []
        for symbol in Q_old_val.free_symbols:
            subsList.append([symbol, 100000])
        Q_old_val = Q_old_val.subs(subsList)

        return Q_new_val > Q_old_val

    else:
        return True


def compare_st(subgraph_st, subgraph_opt, Q_old_val=-1):
    Ss = sp.sympify("Ss")
    Q_new_val = subgraph_st.Q.subs(Ss, 10000)
    subsList = []
    for symbol in Q_new_val.free_symbols:
        subsList.append([symbol, 100000])
    Q_new_val = Q_new_val.subs(subsList)

    if Q_old_val == -1:
        Q_old_val = subgraph_opt.Q.subs(Ss, 10000)
        subsList = []
        for symbol in Q_old_val.free_symbols:
            subsList.append([symbol, 100000])
        Q_old_val = Q_old_val.subs(subsList)

    # decide which subgraph is larger (we prefer larger merges)
    if len(subgraph_st.name.split(";")) >= len(subgraph_opt.name.split(";")):
        larger_subgraph = subgraph_st
        larger_sg_Q = Q_new_val
        smaller_subgraph = subgraph_opt
        smaller_sg_Q = Q_old_val
    else:
        larger_subgraph = subgraph_opt
        larger_sg_Q = Q_old_val
        smaller_subgraph = subgraph_st
        smaller_sg_Q = Q_new_val

    # smaller subgraph must have much smaller Q to be preferable:
    if smaller_sg_Q != 0 and (1.2 * smaller_sg_Q < larger_sg_Q):
        return [smaller_subgraph, smaller_sg_Q]
    else:
        return [larger_subgraph, larger_sg_Q]


def rng_to_subset(ranges: dict):
    iter_vars = list(map(dace.symbol, [v for v in ranges.keys()]))
    return [(i, i, 1) for i in iter_vars]


def d2sp(expression):
    return sp.sympify(str(expression).replace("N", "n"))


def extract_access(accessFun, itervars):
    # remove parameters from the access function (e.g., A[N*i] -> A[i])
    allVars = accessFun.free_symbols
    params = allVars - itervars
    if params != allVars:
        for param in params:
            accessFun = accessFun.subs(param, 1)
    else:
        return [None, None]

    accessPol = sp.Poly(accessFun)
    accessVars = accessPol.gens
    baseAccess = sp.sympify(0)
    offset = sp.sympify(0)
    for k, c in zip(accessPol.monoms(), accessPol.coeffs()):
        monom = c * sp.prod(x**k1 for x, k1 in zip(accessVars, k))
        if sum(k) > 0:
            baseAccess += monom
        else:
            offset = monom
    baseAccess = sp.prod(baseAccess.free_symbols)

    # if the access has more than one iteration variable (e.g., A[k - i]), we replace it with A[k,i])
    # then, the dimension of the offset must match
    offset = [offset] * len(baseAccess.free_symbols)
    return [baseAccess, offset]


def get_lead_term(expression):
    q_pol = sp.Poly(expression)
    q_vars = list(q_pol.gens)
    q_monoms = [list(monom) for monom in q_pol.monoms()]
    q_coeffs = list(q_pol.coeffs())

    # check if one of the generators is 1/S (instead of S). Then, we need to flip it.
    S = sp.sympify("Ss")
    for i in range(len(q_vars)):
        if q_vars[i] == S:
            a = 1

        if q_vars[i] == 1 / S:
            q_vars[i] = S
            for monom in q_monoms:
                monom[i] = -monom[i]

    max_deg = max([sum(monom) for monom in q_monoms])
    simpQ = sp.sympify(0)
    for k, c in zip(q_monoms, q_coeffs):
        if sum(k) >= max_deg:
            monom = c * sp.prod(x**k1 for x, k1 in zip(q_vars, k))
            simpQ += monom
    return simpQ


# Checks whether two base accessses are the same. It is NOT enough to just have
# a string comparison (e.g., "i*j" == "i*j"), as sometimes the same iteration variables
# have different names (e.g., A[dace_tmp_3] == A[dace_tmp_4] in jacobi1d)
def eq_accesses(base_access1, base_access2):
    accesses_1 = base_access1.split("*")
    accesses_2 = base_access2.split("*")
    if any((acc1 in accesses_2) for acc1 in accesses_1):
        return base_access1 == base_access2
    else:
        # if there are no common iteration variables, we conservatively assume they are the same
        # (e.g., A[dace_tmp_3] == A[dace_tmp_4])
        return len(accesses_1) == len(accesses_2)
